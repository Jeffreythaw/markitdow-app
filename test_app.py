from io import BytesIO

from app import app


def post_file(client, content, name):
    return client.post(
        "/",
        data={"file": (BytesIO(content), name)},
        content_type="multipart/form-data",
    )


def main():
    client = app.test_client()

    ok = post_file(client, b"name,value\na,1\n", "sample.csv")
    assert ok.status_code == 200
    assert b"name" in ok.data
    assert b"value" in ok.data

    bad = post_file(client, b"x", "bad.exe")
    assert bad.status_code == 200
    assert "ဒီ file type ကို မထောက်ပံ့သေးပါ။".encode() in bad.data

    image = post_file(client, b"\x89PNG\r\n\x1a\n", "sample.png")
    assert image.status_code == 200
    assert b"sample.png" in image.data
    assert "OCR သို့မဟုတ် Vision LLM".encode() in image.data


if __name__ == "__main__":
    main()
    print("app checks passed")
