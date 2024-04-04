CREW_CHOICES = (
	("keeping", "심사중"),
	("member", "승인"),
	("not_member", "미승인"),
)

GENDER_CHOICES = (
    ("none", "선택안함"),
    ("female", "여자"),
    ("male", "남자"),
)

USER_TYPE_CHOICES = (
    ("normal", "일반"),
    ("crew", "크루장"),
)

LOCATION_CITY_CHOICES = (
    ("seoul", "서울"),
    ("gyeonggi", "경기"),
    ("gangwon", "강원"),
    ("chungcheong", "충청"),
    ("jeolla", "전라"),
    ("gyeongsang", "경상"),
    ("jeju", "제주"),
    ("etc", "기타"),
)

MEET_DAY_CHOICES = (
    ("mon", "월"),
    ("tue", "화"),
    ("wed", "수"),
    ("thu", "목"),
    ("fri", "금"),
    ("sat", "토"),
    ("sun", "일"),
)

TIME_CHOICES = [
    (f"{hour:02d}:{minute:02d} {"AM" if hour < 12 else "PM"}", f"{hour % 12 or 12:02d}:{minute:02d} {"AM" if hour < 12 else "PM"}")
    for hour in range(24)
    for minute in (0, 30)
]

COURSE_CHOICES = (
        (42195, "Full"),
        (21097, "Half"),
        (10000, "10km"),
        (5000, "5km"),
        (3000, "3km"),
)

STATUS_CHOICES = (
        (0, "모집중"),    # 모집중
        (1, "모집예정"),    # 모집예정 
        (2, "모집마감"),    # 모집마감 
)