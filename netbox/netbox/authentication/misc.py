# Copyright (c) 2009, Peter Sagerson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from users.models import Group


# Copied from django_auth_ldap.backend._LDAPUser and modified to support our
# custom Group model.
def _mirror_groups(self):
    """
    Mirrors the user's LDAP groups in the Django database and updates the
    user's membership.
    """
    target_group_names = frozenset(self._get_groups().get_group_names())
    current_group_names = frozenset(
        self._user.groups.values_list("name", flat=True).iterator()
    )

    # These were normalized to sets above.
    MIRROR_GROUPS_EXCEPT = self.settings.MIRROR_GROUPS_EXCEPT
    MIRROR_GROUPS = self.settings.MIRROR_GROUPS

    # If the settings are white- or black-listing groups, we'll update
    # target_group_names such that we won't modify the membership of groups
    # beyond our purview.
    if isinstance(MIRROR_GROUPS_EXCEPT, (set, frozenset)):
        target_group_names = (target_group_names - MIRROR_GROUPS_EXCEPT) | (
            current_group_names & MIRROR_GROUPS_EXCEPT
        )
    elif isinstance(MIRROR_GROUPS, (set, frozenset)):
        target_group_names = (target_group_names & MIRROR_GROUPS) | (
            current_group_names - MIRROR_GROUPS
        )

    if target_group_names != current_group_names:
        existing_groups = list(
            Group.objects.filter(name__in=target_group_names).iterator()
        )
        existing_group_names = frozenset(group.name for group in existing_groups)

        new_groups = [
            Group.objects.get_or_create(name=name)[0]
            for name in target_group_names
            if name not in existing_group_names
        ]

        self._user.groups.set(existing_groups + new_groups)
