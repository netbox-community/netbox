from users.preferences import UserPreference


preferences = {
    'pref1': UserPreference(
        label='First preference',
        choices=(
            ('foo', 'Foo'),
            ('bar', 'Bar'),
        )
    ),
    'pref2': UserPreference(
        label='Second preference',
        choices=(
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
        )
    ),
}
