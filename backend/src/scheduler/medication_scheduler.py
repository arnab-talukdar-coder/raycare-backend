from src.common.logger import get_logger
from src.common.responses import ok
from src.services.reminder_service import run_due_reminders

logger = get_logger(__name__)


def lambda_handler(event, context):
    logger.info("Running medication reminder scheduler")
    return ok(run_due_reminders())
