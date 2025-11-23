from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.call_schedule import CallScheduleService
from app.services.call import CallService
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스
scheduler = AsyncIOScheduler()


async def schedule_calls():
    """
    매 시간 55분에 실행
    
    다음 1시간 동안 예정된 통화 스케줄을 조회하고 APScheduler에 등록
    """
    logger.info(f"Scheduling calls for next hour at {datetime.now()}")
    
    try:
        # 데이터베이스 세션 생성
        async for db in get_db():
            # 다음 1시간 동안 예정된 통화 스케줄 조회
            schedules = await CallScheduleService.get_scheduled_calls_for_next_hour(db)
            
            logger.info(f"Found {len(schedules)} scheduled calls for next hour")
            
            # 각 스케줄에 대해 통화 작업 예약
            for elder_id, run_time in schedules:
                
                # APScheduler에 작업 추가
                job_id = f"call_{elder_id}_{run_time.strftime('%Y%m%d_%H%M')}"
                
                scheduler.add_job(
                    initiate_call,
                    trigger='date',
                    run_date=run_time,
                    args=[elder_id],
                    id=job_id,
                    replace_existing=True
                )
                
                logger.info(f"Scheduled call for elder {elder_id} at {run_time}")
            
            break  # get_db()는 generator이므로 한 번만 실행
        
        logger.info("Calls scheduled successfully")
    except Exception as e:
        logger.error(f"Error in schedule_calls: {str(e)}", exc_info=True)




async def initiate_call(elder_id: int):
    async with AsyncSessionLocal() as db:
        try:
            result = await CallService.initiate_call(db, elder_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Error initiating call: {e}", exc_info=True)
            raise


def start_scheduler():
    """
    스케줄러 시작
    """
    try:

        scheduler.add_job(
            schedule_calls,
            trigger=CronTrigger(minute=55), # every hour
            id="schedule_calls",
            name="Schedule calls within the next hour",
            replace_existing=True
        )
        
        # 스케줄러 시작
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        # 등록된 작업 목록 출력
        jobs = scheduler.get_jobs()
        for job in jobs:
            logger.info(f"Scheduled job: {job.id} - Next run: {job.next_run_time}")
            
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)


def shutdown_scheduler():
    """
    스케줄러 종료
    """
    try:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")
    except Exception as e:
        logger.error(f"Failed to shutdown scheduler: {str(e)}", exc_info=True)

