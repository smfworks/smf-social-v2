"""APScheduler setup for SMF Social v2.

Free, embedded, persists to SQLite.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy import create_engine
from datetime import datetime
import logging

from core.config import DATABASE_URL
from core.database import get_db
from core.security import decrypt_token
from models.sqlite_database import Post, Integration

# Setup logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Job store in same SQLite database
jobstores = {
    'default': SQLAlchemyJobStore(url=DATABASE_URL, tablename='scheduler_jobs')
}

# Thread pool for concurrent jobs
executors = {
    'default': ThreadPoolExecutor(max_workers=5)
}

# Job defaults
job_defaults = {
    'coalesce': True,  # Catch up missed jobs
    'max_instances': 1,  # Only one instance of each job
    'misfire_grace_time': 3600  # Run if delayed up to 1 hour
}

# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get or create scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
    return _scheduler

def start_scheduler():
    """Start the scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler started")

def stop_scheduler():
    """Stop the scheduler."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
        print("⏹️  Scheduler stopped")

def schedule_post(post_id: str, scheduled_for: datetime):
    """Schedule a post for future publication.
    
    Args:
        post_id: UUID of post to schedule
        scheduled_for: When to publish
    """
    scheduler = get_scheduler()
    
    job_id = f'post_{post_id}'
    
    # Remove existing job if any
    try:
        scheduler.remove_job(job_id)
    except:
        pass
    
    # Add new job
    scheduler.add_job(
        func=publish_scheduled_post,
        trigger='date',
        run_date=scheduled_for,
        args=[post_id],
        id=job_id,
        replace_existing=True,
        misfire_grace_time=3600
    )
    
    print(f"📅 Scheduled post {post_id} for {scheduled_for}")

def cancel_scheduled_post(post_id: str):
    """Cancel a scheduled post.
    
    Args:
        post_id: UUID of post to cancel
    """
    scheduler = get_scheduler()
    job_id = f'post_{post_id}'
    
    try:
        scheduler.remove_job(job_id)
        print(f"🚫 Cancelled scheduled post {post_id}")
    except:
        pass

def publish_scheduled_post(post_id: str):
    """Publish a scheduled post.
    
    This function is called by the scheduler.
    It runs in a separate thread.
    """
    print(f"🚀 Publishing scheduled post {post_id}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get post
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            print(f"❌ Post {post_id} not found")
            return
        
        if post.status != 'scheduled':
            print(f"⚠️ Post {post_id} is not scheduled (status: {post.status})")
            return
        
        # Get integration
        integration = post.integration
        if not integration or not integration.is_active:
            post.status = 'failed'
            post.error_message = 'Integration not available'
            db.commit()
            print(f"❌ Integration not available for post {post_id}")
            return
        
        # Decrypt token
        access_token = decrypt_token(integration.access_token)
        
        # Get provider
        from providers.pinterest import PinterestProvider
        from providers.linkedin import LinkedInProvider
        
        oauth_app = integration.oauth_app
        credentials = {
            'client_id': oauth_app.client_id,
            'client_secret': oauth_app.client_secret,
            'redirect_uri': oauth_app.redirect_uri
        }
        
        # Post to platform
        if integration.platform == 'pinterest':
            provider = PinterestProvider(credentials)
            result = provider.post(
                content=post.content,
                access_token=access_token,
                media_urls=post.media_urls,
                board_id=integration.settings.get('board_id') if integration.settings else None
            )
        elif integration.platform == 'linkedin':
            provider = LinkedInProvider(credentials)
            # LinkedIn requires UGC API implementation
            raise NotImplementedError("LinkedIn posting not yet implemented")
        else:
            raise NotImplementedError(f"Platform {integration.platform} not implemented")
        
        # Update post
        post.status = 'published'
        post.published_at = datetime.utcnow()
        post.platform_post_id = result.get('post_id')
        post.platform_url = result.get('url')
        post.platform_response = result.get('platform_response')
        
        # Update integration last used
        integration.last_used_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Published post {post_id}: {result.get('url')}")
        
    except Exception as e:
        print(f"❌ Failed to publish post {post_id}: {e}")
        
        # Update post status
        post.status = 'failed'
        post.error_message = str(e)
        db.commit()
        
        # Could retry here with exponential backoff
        # For now, just fail
    
    finally:
        db.close()
