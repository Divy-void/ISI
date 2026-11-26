from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_demo_login_and_rbac():
    with TestClient(app) as c:
        res = c.post("/api/auth/demo-login", json={"role": "procurement_officer"})
        assert res.status_code == 200
        assert res.json()["role"] == "procurement_officer"

        # Non-admin cannot access admin endpoints
        res_forbidden = c.get("/api/admin/users", headers={"X-Demo-Role": "procurement_officer"})
        assert res_forbidden.status_code == 403

        # Admin can access admin endpoints
        res_admin = c.get("/api/admin/users", headers={"X-Demo-Role": "admin"})
        assert res_admin.status_code == 200
        assert len(res_admin.json()) >= 3


def test_sample_tender_end_to_end():
    with TestClient(app) as c:
        headers = {"X-Demo-Role": "procurement_officer"}
        # 1. Create sample analysis
        create_res = c.post(
            "/api/analyses",
            json={
                "title": "Municipal Outdoor LED Street Lighting Procurement",
                "category": "Lighting",
                "department_name": "Municipal Electrical & Lighting",
                "is_sample": True,
            },
            headers=headers,
        )
        assert create_res.status_code == 200
        analysis_id = create_res.json()["id"]

        # 2. Process & extract requirements
        proc_res = c.post(f"/api/analyses/{analysis_id}/process", headers=headers)
        assert proc_res.status_code == 200
        assert proc_res.json()["extracted_count"] >= 5

        # 3. Generate recommendations
        rec_res = c.post(f"/api/analyses/{analysis_id}/recommend", headers=headers)
        assert rec_res.status_code == 200
        assert rec_res.json()["count"] >= 1

        # 4. Get recommendations & coverage
        recs = c.get(f"/api/analyses/{analysis_id}/recommendations", headers=headers).json()
        assert len(recs) >= 1
        assert recs[0]["standard"]["catalogue_id"].startswith("DEMO-STD-")

        cov = c.get(f"/api/analyses/{analysis_id}/coverage", headers=headers).json()
        assert len(cov["rows"]) >= 5
        assert len(cov["columns"]) >= 1

        # 5. Save reviewer decision
        dec_res = c.post(
            f"/api/recommendations/{recs[0]['id']}/decision",
            json={"decision": "accepted", "comments": "Verified for demo"},
            headers=headers,
        )
        assert dec_res.status_code == 200

        # 6. Generate report & export CSV
        rpt_res = c.post(f"/api/analyses/{analysis_id}/reports", headers=headers)
        assert rpt_res.status_code == 200
        report_id = rpt_res.json()["id"]

        csv_res = c.get(f"/api/reports/{report_id}/csv", headers=headers)
        assert csv_res.status_code == 200
        assert "DEMO-STD-" in csv_res.text


def test_standards_search():
    with TestClient(app) as c:
        res = c.get("/api/standards/search?q=led")
        assert res.status_code == 200
        assert len(res.json()) >= 1
