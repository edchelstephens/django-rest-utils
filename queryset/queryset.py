from django.db.models import QuerySet


class ActiveQuerySet(QuerySet):
    """Active query set for models with is_active boolean field."""
    def actives(self) -> QuerySet:
        """Filter only actives queryset."""
        return self.filter(is_active=True)
