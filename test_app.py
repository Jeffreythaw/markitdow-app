from io import BytesIO
from unittest.mock import patch

from app import app


class FakeOpenAI:
    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                class Message:
                    content = "Visible text from image"

                class Choice:
                    message = Message()

                class Response:
                    choices = [Choice()]

                return Response()


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

    with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
        image = post_file(client, b"\x89PNG\r\n\x1a\n", "sample.png")
    assert image.status_code == 200
    assert b"sample.png" in image.data
    assert b"OPENAI_API_KEY" in image.data

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}), patch(
        "app.OpenAI", FakeOpenAI
    ):
        vision = post_file(client, b"\xff\xd8\xff", "sample.jpeg")
    assert vision.status_code == 200
    assert b"Visible text from image" in vision.data


if __name__ == "__main__":
    main()
    print("app checks passed")
