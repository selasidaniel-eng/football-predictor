"""Seed script to populate the database with initial data."""

import asyncio
from datetime import datetime, timedelta
from random import randint, shuffle, choice
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models import League, Team, Match, Injury
from app.seeds.data import LEAGUES_DATA, TEAMS_DATA

settings = get_settings()


async def seed_leagues(session: AsyncSession):
    """Seed leagues into the database."""
    print("📚 Seeding leagues...")
    
    for league_data in LEAGUES_DATA:
        result = await session.execute(
            select(League).filter(League.name == league_data["name"])
        )
        if result.scalars().first():
            print(f"  ⏭️  Skipping {league_data['name']} (already exists)")
            continue
        
        league = League(**league_data)
        session.add(league)
        print(f"  ✅ Added: {league_data['name']}")
    
    await session.commit()
    print(f"✅ Leagues seeded successfully!\n")


async def seed_teams(session: AsyncSession):
    """Seed teams into the database."""
    print("🏟️  Seeding teams...")
    
    for league_name, teams_list in TEAMS_DATA.items():
        # Get the league
        result = await session.execute(
            select(League).filter(League.name == league_name)
        )
        league = result.scalars().first()
        
        if not league:
            print(f"  ⚠️  League '{league_name}' not found, skipping teams")
            continue
        
        for team_data in teams_list:
            result = await session.execute(
                select(Team).filter(Team.name == team_data["name"])
            )
            if result.scalars().first():
                print(f"  ⏭️  Skipping {team_data['name']} (already exists)")
                continue
            
            team = Team(league_id=league.id, **team_data)
            session.add(team)
            print(f"  ✅ Added: {team_data['name']} ({league_name})")
    
    await session.commit()
    print(f"✅ Teams seeded successfully!\n")


async def seed_matches(session: AsyncSession):
    """Seed match fixtures for the season."""
    print("⚽ Seeding matches...")
    
    # Get all leagues with their teams
    result = await session.execute(select(League))
    leagues = result.scalars().all()
    
    match_count = 0
    
    for league in leagues:
        # Get teams for this league
        result = await session.execute(
            select(Team).filter(Team.league_id == league.id)
        )
        teams = result.scalars().all()
        
        if len(teams) < 2:
            continue
        
        print(f"  📅 Generating fixtures for {league.name}...")
        
        # Generate round-robin fixtures (each team plays each other home and away)
        fixtures = []
        for i, home_team in enumerate(teams):
            for away_team in teams:
                if home_team.id != away_team.id:
                    fixtures.append((home_team, away_team))
        
        # Shuffle to randomize order
        shuffle(fixtures)
        
        # Create match objects starting from 2025-08-15
        start_date = datetime(2025, 8, 15)
        
        for match_week, (home_team, away_team) in enumerate(fixtures[:20], start=1):  # Limit to 20 matches per league
            match_date = start_date + timedelta(days=(match_week - 1) * 4)
            
            # Check if match already exists
            result = await session.execute(
                select(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.match_date == match_date
                )
            )
            if result.scalars().first():
                continue
            
            match = Match(
                league_id=league.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date,
                match_week=match_week,
                venue=home_team.stadium,
                referee="TBD",
                home_odds=choice([1.80, 1.85, 1.90, 1.95, 2.00]),
                draw_odds=choice([3.20, 3.30, 3.40, 3.50]),
                away_odds=choice([3.50, 3.75, 4.00, 4.25, 4.50]),
                status="scheduled"
            )
            session.add(match)
            match_count += 1
        
        print(f"    ✅ Created {match_count} matches for {league.name}")
    
    await session.commit()
    print(f"✅ Matches seeded successfully! (Total: {match_count})\n")


async def seed_injuries(session: AsyncSession):
    """Seed some sample injuries."""
    print("🏥 Seeding injuries...")
    
    # Get some teams
    result = await session.execute(select(Team).limit(5))
    teams = result.scalars().all()
    
    injury_count = 0
    
    for team in teams:
        for i in range(randint(1, 3)):
            injury = Injury(
                team_id=team.id,
                player_name=f"Player {i+1}",
                position=choice(["Goalkeeper", "Defender", "Midfielder", "Forward"]),
                severity=choice(["Minor", "Moderate", "Severe"]),
                injury_date=datetime.now() - timedelta(days=randint(1, 30)),
                expected_return=datetime.now() + timedelta(days=randint(5, 60)),
                impact_score=randint(1, 10)
            )
            session.add(injury)
            injury_count += 1
    
    await session.commit()
    print(f"✅ Injuries seeded successfully! (Total: {injury_count})\n")


async def main():
    """Main seeding function."""
    print("\n" + "="*60)
    print("🌱 FOOTBALL PREDICTOR - DATABASE SEEDING")
    print("="*60 + "\n")
    
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
            # Seed data in order
            await seed_leagues(session)
            await seed_teams(session)
            await seed_matches(session)
            await seed_injuries(session)
            
            print("="*60)
            print("✅ DATABASE SEEDING COMPLETE!")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
