"""Data access layer for pairwise card rankings."""

from datetime import UTC, datetime
from itertools import combinations

from mtgdb import UserRanking, UserRankingComparison, UserRankingExclusion, get_session
from sqlmodel import func, select


def _ranking_to_dict(ranking: UserRanking, comparison_count: int = 0) -> dict:
    return {
        "id": ranking.id,
        "name": ranking.name,
        "filters": ranking.filters or {},
        "comparison_count": comparison_count,
        "created_at": ranking.created_at.isoformat() if ranking.created_at else "",
        "updated_at": ranking.updated_at.isoformat() if ranking.updated_at else "",
    }


class RankingsData:
    def create_ranking(self, name: str, filters: dict) -> dict:
        with get_session() as session:
            ranking = UserRanking(name=name, filters=filters)
            session.add(ranking)
            session.commit()
            session.refresh(ranking)
            return _ranking_to_dict(ranking)

    def list_rankings(self) -> list[dict]:
        with get_session() as session:
            rankings = session.exec(select(UserRanking).order_by(UserRanking.updated_at.desc())).all()
            counts = dict(
                session.exec(
                    select(UserRankingComparison.ranking_id, func.count()).group_by(UserRankingComparison.ranking_id)
                ).all()
            )
            return [_ranking_to_dict(r, counts.get(r.id, 0)) for r in rankings]

    def get_ranking(self, ranking_id: int) -> dict | None:
        with get_session() as session:
            ranking = session.get(UserRanking, ranking_id)
            if not ranking:
                return None
            comparisons = session.exec(
                select(UserRankingComparison)
                .where(UserRankingComparison.ranking_id == ranking_id)
                .order_by(UserRankingComparison.id)
            ).all()
            result = _ranking_to_dict(ranking, len(comparisons))
            result["comparisons"] = [{"winner_name": c.winner_name, "loser_name": c.loser_name} for c in comparisons]
            result["excluded_names"] = session.exec(
                select(UserRankingExclusion.card_name)
                .where(UserRankingExclusion.ranking_id == ranking_id)
                .order_by(UserRankingExclusion.card_name)
            ).all()
            return result

    def add_round(self, ranking_id: int, ordered_card_names: list[str]) -> int | None:
        """Record every pair implied by a best-to-worst ordering; returns the number of comparisons added."""
        with get_session() as session:
            ranking = session.get(UserRanking, ranking_id)
            if not ranking:
                return None
            pairs = list(combinations(ordered_card_names, 2))
            for winner, loser in pairs:
                session.add(UserRankingComparison(ranking_id=ranking_id, winner_name=winner, loser_name=loser))
            ranking.updated_at = datetime.now(UTC)
            session.commit()
            return len(pairs)

    def exclude_card(self, ranking_id: int, card_name: str) -> bool | None:
        """Leave a card out of the ranking; None if the ranking is unknown. Excluding twice is a no-op."""
        with get_session() as session:
            ranking = session.get(UserRanking, ranking_id)
            if not ranking:
                return None
            existing = session.exec(
                select(UserRankingExclusion).where(
                    UserRankingExclusion.ranking_id == ranking_id, UserRankingExclusion.card_name == card_name
                )
            ).first()
            if not existing:
                session.add(UserRankingExclusion(ranking_id=ranking_id, card_name=card_name))
                ranking.updated_at = datetime.now(UTC)
                session.commit()
            return True

    def restore_card(self, ranking_id: int, card_name: str) -> bool:
        with get_session() as session:
            exclusion = session.exec(
                select(UserRankingExclusion).where(
                    UserRankingExclusion.ranking_id == ranking_id, UserRankingExclusion.card_name == card_name
                )
            ).first()
            if not exclusion:
                return False
            session.delete(exclusion)
            session.commit()
            return True

    def delete_ranking(self, ranking_id: int) -> bool:
        with get_session() as session:
            ranking = session.get(UserRanking, ranking_id)
            if not ranking:
                return False
            comparisons = session.exec(
                select(UserRankingComparison).where(UserRankingComparison.ranking_id == ranking_id)
            ).all()
            exclusions = session.exec(
                select(UserRankingExclusion).where(UserRankingExclusion.ranking_id == ranking_id)
            ).all()
            for row in [*comparisons, *exclusions]:
                session.delete(row)
            session.delete(ranking)
            session.commit()
            return True


rankings_data = RankingsData()
