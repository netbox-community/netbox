import strawberry
import strawberry_django
from strawberry import auto


class ChangeLoggedModelFilter:

    def created_by_request(self, queryset):
        return self.filter_by_request(queryset, "created_by_request", self.created_by_request)

    def updated_by_request(self, queryset):
        return self.filter_by_request(queryset, "updated_by_request", self.updated_by_request)

    def modified_by_request(self, queryset):
        return self.filter_by_request(queryset, "modified_by_request", self.modified_by_request)


class NetBoxModelFilter(ChangeLoggedModelFilter):

    def filter_q(self, queryset):
        return self.search(queryset, None, self.q)
