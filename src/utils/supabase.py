from db.client import get_client


def refresh_pre_processing() -> None:
    get_client().rpc("refresh_pre_processing").execute()
