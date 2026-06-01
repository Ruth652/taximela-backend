from datetime import datetime, timedelta
from sqlalchemy import text


class AdminAnalyticsRepository:

    def __init__(self, db):
        self.db = db

    def get_total_users(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar()

    def get_total_businesses(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM businesses")
        ).scalar()

    def get_total_registrations(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM business_registrations")
        ).scalar()

    def get_total_contributions(self):
        return self.db.execute(
            text("SELECT COUNT(*) FROM contributions")
        ).scalar()

    def get_contribution_trend(self, period: str):

        now = datetime.utcnow()

        if period == "weekly":

            start_date = now - timedelta(days=6)

            trend_rows = self.db.execute(
                text("""
                    SELECT
                        DATE(created_at) AS day,
                        COUNT(*) AS count
                    FROM contributions
                    WHERE created_at >= :start_date
                    GROUP BY DATE(created_at)
                    ORDER BY day
                """),
                {"start_date": start_date}
            ).mappings().all()

            trend_map = {
                row["day"]: row["count"]
                for row in trend_rows
            }

            trend = []

            for i in range(7):
                day = (start_date + timedelta(days=i)).date()

                trend.append({
                    "label": day.strftime("%a"),
                    "count": trend_map.get(day, 0)
                })

        else:  # monthly

            start_date = datetime(now.year, now.month, 1)

            # go back 11 months
            year = start_date.year
            month = start_date.month - 11

            while month <= 0:
                month += 12
                year -= 1

            start_date = datetime(year, month, 1)

            trend_rows = self.db.execute(
                text("""
                    SELECT
                        DATE_TRUNC('month', created_at) AS month,
                        COUNT(*) AS count
                    FROM contributions
                    WHERE created_at >= :start_date
                    GROUP BY month
                    ORDER BY month
                """),
                {"start_date": start_date}
            ).mappings().all()

            trend_map = {
                (
                    row["month"].year,
                    row["month"].month
                ): row["count"]
                for row in trend_rows
            }

            trend = []

            current_year = start_date.year
            current_month = start_date.month

            for _ in range(12):

                trend.append({
                    "label": datetime(
                        current_year,
                        current_month,
                        1
                    ).strftime("%b"),
                    "count": trend_map.get(
                        (current_year, current_month),
                        0
                    )
                })

                current_month += 1

                if current_month > 12:
                    current_month = 1
                    current_year += 1

        total = self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM contributions
                WHERE created_at >= :start_date
            """),
            {"start_date": start_date}
        ).scalar()

        status_rows = self.db.execute(
            text("""
                SELECT status, COUNT(*) AS count
                FROM contributions
                WHERE created_at >= :start_date
                GROUP BY status
            """),
            {"start_date": start_date}
        ).mappings().all()

        status_breakdown = {
            "pending_review": 0,
            "approved": 0,
            "rejected": 0
        }

        for row in status_rows:
            status_breakdown[row["status"]] = row["count"]

        target_rows = self.db.execute(
            text("""
                SELECT target_type, COUNT(*) AS count
                FROM contributions
                WHERE created_at >= :start_date
                GROUP BY target_type
            """),
            {"start_date": start_date}
        ).mappings().all()

        target_breakdown = {
            "route": 0,
            "station": 0
        }

        for row in target_rows:
            target_breakdown[row["target_type"]] = row["count"]

        return {
            "period": period,
            "start_date": start_date.date().isoformat(),
            "end_date": now.date().isoformat(),
            "total": total,
            "trend": trend,
            "breakdown": {
                "status": status_breakdown,
                "target_type": target_breakdown
            }
        }