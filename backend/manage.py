#!/usr/bin/env python
"""CLI tool to manage database seeding and initialization."""

import asyncio
import click
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import init_db
from app.seeds.seed import seed_leagues, seed_teams, seed_matches, seed_injuries

settings = get_settings()


@click.group()
def cli():
    """Football Predictor Database Management CLI."""
    pass


@cli.command()
@click.option("--skip-leagues", is_flag=True, help="Skip seeding leagues")
@click.option("--skip-teams", is_flag=True, help="Skip seeding teams")
@click.option("--skip-matches", is_flag=True, help="Skip seeding matches")
@click.option("--skip-injuries", is_flag=True, help="Skip seeding injuries")
def seed(skip_leagues, skip_teams, skip_matches, skip_injuries):
    """Seed the database with initial data."""
    click.echo("\n" + "="*60)
    click.echo("🌱 FOOTBALL PREDICTOR - DATABASE SEEDING")
    click.echo("="*60 + "\n")
    
    async def run():
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
        )
        
        # Create async session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        try:
            async with async_session() as session:
                if not skip_leagues:
                    await seed_leagues(session)
                else:
                    click.echo("⏭️  Skipping league seeding\n")
                
                if not skip_teams:
                    await seed_teams(session)
                else:
                    click.echo("⏭️  Skipping team seeding\n")
                
                if not skip_matches:
                    await seed_matches(session)
                else:
                    click.echo("⏭️  Skipping match seeding\n")
                
                if not skip_injuries:
                    await seed_injuries(session)
                else:
                    click.echo("⏭️  Skipping injury seeding\n")
                
                click.echo("="*60)
                click.echo("✅ DATABASE SEEDING COMPLETE!")
                click.echo("="*60 + "\n")
        
        except Exception as e:
            click.echo(f"\n❌ Error during seeding: {e}", err=True)
            raise
        finally:
            await engine.dispose()
    
    asyncio.run(run())


@cli.command()
def init():
    """Initialize database tables (creates tables from models)."""
    click.echo("\n" + "="*60)
    click.echo("🗄️  INITIALIZING DATABASE TABLES")
    click.echo("="*60 + "\n")
    
    async def run():
        from app.core.database import init_db
        
        try:
            await init_db()
            click.echo("✅ DATABASE TABLES CREATED SUCCESSFULLY!")
            click.echo("="*60 + "\n")
        except Exception as e:
            click.echo(f"\n❌ Error during initialization: {e}", err=True)
            raise
    
    asyncio.run(run())


@cli.command()
def reset():
    """Reset the database (drop all tables and recreate)."""
    click.echo("\n⚠️  WARNING: This will DELETE all data from the database!")
    if not click.confirm("Are you sure you want to continue?"):
        click.echo("❌ Database reset cancelled.")
        return
    
    click.echo("\n" + "="*60)
    click.echo("🗑️  RESETTING DATABASE")
    click.echo("="*60 + "\n")
    
    async def run():
        from sqlalchemy import text
        from app.core.database import engine as db_engine
        from app.models import Base
        
        try:
            async with db_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                click.echo("✅ All tables dropped")
                
                await conn.run_sync(Base.metadata.create_all)
                click.echo("✅ All tables recreated")
            
            click.echo("\n" + "="*60)
            click.echo("✅ DATABASE RESET COMPLETE!")
            click.echo("Next: Run 'python manage.py seed' to populate with data")
            click.echo("="*60 + "\n")
        except Exception as e:
            click.echo(f"\n❌ Error during reset: {e}", err=True)
            raise
    
    asyncio.run(run())


@cli.command()
def full_setup():
    """Complete setup: initialize tables and seed data."""
    click.echo("\n" + "="*60)
    click.echo("🚀 FULL DATABASE SETUP")
    click.echo("="*60 + "\n")
    
    async def run():
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
        )
        
        # Create async session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        try:
            # Initialize tables
            click.echo("Step 1: Initializing tables...")
            await init_db()
            click.echo("✅ Tables created\n")
            
            # Seed data
            async with async_session() as session:
                click.echo("Step 2: Seeding leagues...")
                await seed_leagues(session)
                
                click.echo("Step 3: Seeding teams...")
                await seed_teams(session)
                
                click.echo("Step 4: Seeding matches...")
                await seed_matches(session)
                
                click.echo("Step 5: Seeding injuries...")
                await seed_injuries(session)
            
            click.echo("\n" + "="*60)
            click.echo("✅ FULL SETUP COMPLETE!")
            click.echo("="*60)
            click.echo("\nYou can now:")
            click.echo("  • Start the API: uvicorn app.main:app --reload")
            click.echo("  • Visit Swagger UI: http://localhost:8000/docs")
            click.echo("="*60 + "\n")
        
        except Exception as e:
            click.echo(f"\n❌ Error during setup: {e}", err=True)
            raise
        finally:
            await engine.dispose()
    
    asyncio.run(run())


if __name__ == "__main__":
    cli()
