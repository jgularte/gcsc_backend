from source.chalicelib import auth_service

username = "testuser@gmail.com"
password = "TempPassword24"
newpassword = "NewPassword24"
client_id = "3isa3gbt5oi9j01pos3v0dbqmo"
session = ""


def test_init_auth_flow():
    global session
    resp = auth_service.init_auth_flow(
        client_id=client_id,
        username_hash=username,
        password_hash=password
    )
    assert resp
    session = resp["Session"]
    print(resp)


def test_respond_auth_flow():
    test_init_auth_flow()

    cparams = {
        "USERNAME": username,
        "NEW_PASSWORD": newpassword,
        "userAttributes.name": "Jack",
        "userAttributes.phone_number:": "5098507458",
        "userAttributes.family_name": "Gularte"
    }
    resp = auth_service.respond_auth_flow(
        client_id="3isa3gbt5oi9j01pos3v0dbqmo",
        challenge="NEW_PASSWORD_REQUIRED",
        session=session,
        challenge_params=cparams
    )
    assert resp
    print(resp)