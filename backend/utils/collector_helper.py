from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError


def safe_execute(api_call):

    try:

        if hasattr(api_call, "execute"):
            return api_call.execute()

        return api_call

    except HttpError as e:

        print(f"[Collector] API Error: {e}")

        return None

    except GoogleAPICallError as e:

        print(f"[Collector] API Error: {e}")

        return None

    except Exception as e:

        print(f"[Collector] Error: {e}")

        return None