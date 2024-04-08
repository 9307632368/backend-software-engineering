from fastapi.testclient import TestClient

def test_upload_download_delete(tmp_path, load_example):
    module = load_example("02-file-upload-service")
    with TestClient(module.create_app(tmp_path)) as api:
        saved = api.post("/files", files={"file": ("notes.txt", b"lecture notes", "text/plain")})
        assert saved.status_code == 201
        identifier = saved.json()["id"]
        assert saved.json()["size"] == 13
        assert api.get(f"/files/{identifier}").content == b"lecture notes"
        assert api.delete(f"/files/{identifier}").status_code == 204
        assert api.get(f"/files/{identifier}").status_code == 404

def test_file_checks(tmp_path, load_example):
    module = load_example("02-file-upload-service")
    with TestClient(module.create_app(tmp_path)) as api:
        assert api.post("/files", files={"file": ("program.exe", b"x", "application/octet-stream")}).status_code == 415
        assert api.post("/files", files={"file": ("large.csv", b"x" * (module.MAX_BYTES + 1), "text/csv")}).status_code == 413
        assert list(tmp_path.iterdir()) == []
        assert api.get("/files/missing").status_code == 404

def test_server_generated_filename(tmp_path, load_example):
    module = load_example("02-file-upload-service")
    with TestClient(module.create_app(tmp_path)) as api:
        response = api.post("/files", files={"file": ("../../data.csv", b"id,value\n1,5", "text/csv")})
        assert response.status_code == 201
        assert all(path.parent == tmp_path for path in tmp_path.iterdir())
        assert len(list(tmp_path.iterdir())) == 1
