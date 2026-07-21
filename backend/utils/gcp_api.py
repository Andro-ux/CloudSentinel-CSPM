import logging

from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def safe_execute(request, default=None):

    if default is None:
        default = {}

    try:
        return request.execute()

    except HttpError as e:

        logger.warning(
            "Google API request failed: %s",
            e,
        )

        return default

    except Exception:

        logger.exception(
            "Unexpected Google API error"
        )

        return default