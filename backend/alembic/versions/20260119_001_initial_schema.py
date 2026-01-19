"""Initial schema - create all tables

Revision ID: 20260119_001
Revises: 
Create Date: 2026-01-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260119_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create leagues table
    op.create_table(
        'leagues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leagues_name'), 'leagues', ['name'], unique=True)

    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('stadium', sa.String(length=255), nullable=True),
        sa.Column('home_advantage', sa.Float(), nullable=False),
        sa.Column('strength_rating', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_league_id'), 'teams', ['league_id'])
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'])

    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('home_team_id', sa.Integer(), nullable=False),
        sa.Column('away_team_id', sa.Integer(), nullable=False),
        sa.Column('match_date', sa.DateTime(), nullable=False),
        sa.Column('match_week', sa.Integer(), nullable=True),
        sa.Column('home_goals', sa.Integer(), nullable=True),
        sa.Column('away_goals', sa.Integer(), nullable=True),
        sa.Column('is_finished', sa.Boolean(), nullable=False),
        sa.Column('odds_home_win', sa.Float(), nullable=True),
        sa.Column('odds_draw', sa.Float(), nullable=True),
        sa.Column('odds_away_win', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('referee', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_away_team_id'), 'matches', ['away_team_id'])
    op.create_index(op.f('ix_matches_home_team_id'), 'matches', ['home_team_id'])
    op.create_index(op.f('ix_matches_league_id'), 'matches', ['league_id'])
    op.create_index(op.f('ix_matches_match_date'), 'matches', ['match_date'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create injuries table
    op.create_table(
        'injuries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('player_name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=50), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('injury_date', sa.DateTime(), nullable=False),
        sa.Column('expected_return', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('impact_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_injuries_player_name'), 'injuries', ['player_name'])
    op.create_index(op.f('ix_injuries_team_id'), 'injuries', ['team_id'])

    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('probability_home_win', sa.Float(), nullable=False),
        sa.Column('probability_draw', sa.Float(), nullable=False),
        sa.Column('probability_away_win', sa.Float(), nullable=False),
        sa.Column('expected_goals_home', sa.Float(), nullable=True),
        sa.Column('expected_goals_away', sa.Float(), nullable=True),
        sa.Column('model_confidence', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('prediction_outcome', sa.String(length=50), nullable=True),
        sa.Column('was_correct', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_match_id'), 'predictions', ['match_id'])

    # Create team_form table
    op.create_table(
        'team_form',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('wins_last_5', sa.Integer(), nullable=False),
        sa.Column('draws_last_5', sa.Integer(), nullable=False),
        sa.Column('losses_last_5', sa.Integer(), nullable=False),
        sa.Column('goals_for_last_5', sa.Integer(), nullable=False),
        sa.Column('goals_against_last_5', sa.Integer(), nullable=False),
        sa.Column('wins_last_10', sa.Integer(), nullable=False),
        sa.Column('draws_last_10', sa.Integer(), nullable=False),
        sa.Column('losses_last_10', sa.Integer(), nullable=False),
        sa.Column('goals_for_last_10', sa.Integer(), nullable=False),
        sa.Column('goals_against_last_10', sa.Integer(), nullable=False),
        sa.Column('wins_season', sa.Integer(), nullable=False),
        sa.Column('draws_season', sa.Integer(), nullable=False),
        sa.Column('losses_season', sa.Integer(), nullable=False),
        sa.Column('goals_for_season', sa.Integer(), nullable=False),
        sa.Column('goals_against_season', sa.Integer(), nullable=False),
        sa.Column('average_goals_per_match', sa.Float(), nullable=False),
        sa.Column('average_goals_conceded', sa.Float(), nullable=False),
        sa.Column('form_rating', sa.Float(), nullable=False),
        sa.Column('consistency_score', sa.Float(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id')
    )
    op.create_index(op.f('ix_team_form_team_id'), 'team_form', ['team_id'], unique=True)

    # Create h2h_statistics table
    op.create_table(
        'h2h_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_a_id', sa.Integer(), nullable=False),
        sa.Column('team_b_id', sa.Integer(), nullable=False),
        sa.Column('total_matches', sa.Integer(), nullable=False),
        sa.Column('team_a_wins', sa.Integer(), nullable=False),
        sa.Column('draws', sa.Integer(), nullable=False),
        sa.Column('team_b_wins', sa.Integer(), nullable=False),
        sa.Column('team_a_goals', sa.Integer(), nullable=False),
        sa.Column('team_b_goals', sa.Integer(), nullable=False),
        sa.Column('recent_team_a_wins', sa.Integer(), nullable=False),
        sa.Column('recent_draws', sa.Integer(), nullable=False),
        sa.Column('recent_team_b_wins', sa.Integer(), nullable=False),
        sa.Column('recent_team_a_goals', sa.Integer(), nullable=False),
        sa.Column('recent_team_b_goals', sa.Integer(), nullable=False),
        sa.Column('team_a_home_wins', sa.Integer(), nullable=False),
        sa.Column('team_a_away_wins', sa.Integer(), nullable=False),
        sa.Column('team_a_home_draws', sa.Integer(), nullable=False),
        sa.Column('team_a_away_draws', sa.Integer(), nullable=False),
        sa.Column('team_a_win_rate', sa.Float(), nullable=False),
        sa.Column('team_b_win_rate', sa.Float(), nullable=False),
        sa.Column('average_goals_per_match', sa.Float(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_a_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['team_b_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_h2h_statistics_team_a_id'), 'h2h_statistics', ['team_a_id'])
    op.create_index(op.f('ix_h2h_statistics_team_b_id'), 'h2h_statistics', ['team_b_id'])

    # Create weather_data table
    op.create_table(
        'weather_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('temperature_celsius', sa.Float(), nullable=True),
        sa.Column('feels_like_celsius', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('precipitation_mm', sa.Float(), nullable=True),
        sa.Column('rain_probability', sa.Float(), nullable=True),
        sa.Column('wind_speed_kmh', sa.Float(), nullable=True),
        sa.Column('wind_direction', sa.String(length=50), nullable=True),
        sa.Column('wind_gust_kmh', sa.Float(), nullable=True),
        sa.Column('condition', sa.String(length=100), nullable=True),
        sa.Column('visibility_km', sa.Float(), nullable=True),
        sa.Column('uv_index', sa.Float(), nullable=True),
        sa.Column('pitch_condition', sa.String(length=50), nullable=False),
        sa.Column('field_temperature', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id')
    )
    op.create_index(op.f('ix_weather_data_match_id'), 'weather_data', ['match_id'], unique=True)

    # Create user_predictions table
    op.create_table(
        'user_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('prediction', sa.String(length=50), nullable=False),
        sa.Column('confidence_level', sa.Integer(), nullable=False),
        sa.Column('odds_selected', sa.Float(), nullable=True),
        sa.Column('stake_amount', sa.Float(), nullable=True),
        sa.Column('potential_winnings', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('result', sa.String(length=50), nullable=True),
        sa.Column('is_correct', sa.Integer(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('settled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_predictions_match_id'), 'user_predictions', ['match_id'])
    op.create_index(op.f('ix_user_predictions_user_id'), 'user_predictions', ['user_id'])

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_predictions', sa.Integer(), nullable=False),
        sa.Column('correct_predictions', sa.Integer(), nullable=False),
        sa.Column('win_rate', sa.Float(), nullable=False),
        sa.Column('total_stake', sa.Float(), nullable=False),
        sa.Column('total_winnings', sa.Float(), nullable=False),
        sa.Column('net_profit', sa.Float(), nullable=False),
        sa.Column('roi', sa.Float(), nullable=False),
        sa.Column('favorite_leagues', sa.Text(), nullable=True),
        sa.Column('favorite_teams', sa.Text(), nullable=True),
        sa.Column('preferred_bet_types', sa.Text(), nullable=True),
        sa.Column('max_stake', sa.Float(), nullable=False),
        sa.Column('streak_wins', sa.Integer(), nullable=False),
        sa.Column('streak_losses', sa.Integer(), nullable=False),
        sa.Column('best_streak_wins', sa.Integer(), nullable=False),
        sa.Column('average_odds', sa.Float(), nullable=False),
        sa.Column('prediction_accuracy_trend', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
    
    op.drop_index(op.f('ix_user_predictions_user_id'), table_name='user_predictions')
    op.drop_index(op.f('ix_user_predictions_match_id'), table_name='user_predictions')
    op.drop_table('user_predictions')
    
    op.drop_index(op.f('ix_weather_data_match_id'), table_name='weather_data')
    op.drop_table('weather_data')
    
    op.drop_index(op.f('ix_h2h_statistics_team_b_id'), table_name='h2h_statistics')
    op.drop_index(op.f('ix_h2h_statistics_team_a_id'), table_name='h2h_statistics')
    op.drop_table('h2h_statistics')
    
    op.drop_index(op.f('ix_team_form_team_id'), table_name='team_form')
    op.drop_table('team_form')
    
    op.drop_index(op.f('ix_predictions_match_id'), table_name='predictions')
    op.drop_table('predictions')
    
    op.drop_index(op.f('ix_injuries_team_id'), table_name='injuries')
    op.drop_index(op.f('ix_injuries_player_name'), table_name='injuries')
    op.drop_table('injuries')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_matches_match_date'), table_name='matches')
    op.drop_index(op.f('ix_matches_league_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_home_team_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_away_team_id'), table_name='matches')
    op.drop_table('matches')
    
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_index(op.f('ix_teams_league_id'), table_name='teams')
    op.drop_table('teams')
    
    op.drop_index(op.f('ix_leagues_name'), table_name='leagues')
    op.drop_table('leagues')
