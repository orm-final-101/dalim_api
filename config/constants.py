CREW_CHOICES = (
	('keeping', '심사중'),
	('member', '승인'),
	('not_member', '미승인'),
)

GENDER_CHOICES = (
    ('none', '선택안함'),
    ('female', '여자'),
    ('male', '남자'),
)

USER_TYPE_CHOICES = (
    ('normal', '일반'),
    ('crew', '크루장'),
)

LOCATION_CITY_CHOICES = (
    ('seoul', '서울'),
    ('gyeonggi', '경기'),
    ('gangwon', '강원'),
    ('chungcheong', '충청'),
    ('jeolla', '전라'),
    ('gyeongsang', '경상'),
    ('jeju', '제주'),
    ('etc', '기타'),
)

CATEGORY_CHOICES = (
    ("general", "일반"),
    ("training", "훈련"),
    ("running_gear", "러닝용품"),
    ("end_of_month_sale", "월말결산"),
    ("course_recommendation", "코스추천"),
)

CLASSIFICATION_CHOICES = (
    ("general", "일반"),
    ("event", "이벤트"),
    ("announcement", "공지"),
)