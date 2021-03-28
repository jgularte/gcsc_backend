from source.chalicelib import auth_service

# username = "357ac59a-803e-4be0-a920-49d54cf3e815"
username = "jackfgularte@gmail.com"
password = "NewPassword24"
newpassword = "NewPassword24"
client_id = "59alfspomjihv7js74ba2sjbor"
session = ""


def test_admin_create_user():
    resp = auth_service.admin_create_user(
        user_pool_id="us-west-2_DyOnxCZbx",
        username="jackfgularte@gmail.com",
        temp_password="CapitalPassword24",
        attributes=[
            {
                "Name": "name",
                "Value": "Jack"
            },
            {
                "Name": "family_name",
                "Value": "Gularte"
            },
            {
                "Name": "phone_number",
                "Value": "+15098507458"
            },
            {
                "Name": "email",
                "Value": "jackfgularte@gmail.com"
            }
        ]
    )
    assert resp
    print(resp)


def test_init_auth_flow():
    global session
    resp = auth_service.init_auth_flow(client_id=client_id, username=username, password_hash="CapitalPassword24")
    assert resp
    session = resp["Session"]
    print(resp)


def test_respond_auth_flow():
    global client_id
    test_init_auth_flow()

    cparams = {
        "USERNAME": username,
        "NEW_PASSWORD": newpassword
    }
    resp = auth_service.respond_auth_flow(
        client_id=client_id,
        challenge="NEW_PASSWORD_REQUIRED",
        session=session,
        challenge_params=cparams
    )
    assert resp
    print(resp)