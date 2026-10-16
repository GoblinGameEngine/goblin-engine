extends RefCounted
class_name StationCalendar

## The station's calendar: the ONE place that says what date and what day of the week a game day is.
## Everything that asks "is it a weekday?", "which month?", "what's the date?" asks here (DaySkySystem,
## NpcPlaces.open_on, NpcLife, NpcOccupancy, TransitDemand's events, the Communicator's Date & Time).
##
## The game bible (tools/bible/canon_world.py, "calendar"; remake/bible/world.json):
##   - the Gregorian months and weeks, kept from launch; VY (Voyage Year) counted from launch, 21 April 2252
##     (Launch Day), official since the VY 60 Charter revision; AD kept by the churches and old families;
##   - the present: 2752-05-24, "a Wednesday, VY 500" -- the game opens there.
## The week has run on unbroken aboard for five hundred years, and it is the station's own: Earth's calendar
## would make 2752-05-24 a Saturday. So the weekday is NOT the Gregorian one: it is counted from the
## start, game day 0 = a Wednesday. The dates (months, leap years) are Gregorian.
##
## A game day is DaySkySystem.day: 0 = the start date, 2752-05-24. Weekday numbers are 0 = Monday .. 6 = Sunday
## (as the schedules' "mon-fri" have always counted).
##
## The start date and its weekday are READ from remake/events.json ("start_date", "start_weekday": the station's
## calendar file, tools/make_events.py, which the bible's present date feeds). The constants below are only the
## fallback if that file is missing or unreadable.

const EVENTS := "res://remake/events.json"
const START_Y := 2752                    # (fallbacks: the bible's present date)
const START_M := 5
const START_D := 24
const START_WD := 2                      # day 0 is a Wednesday (0 = Monday)
static var _loaded := false
static var _y := START_Y
static var _m := START_M
static var _d := START_D
static var _wd := START_WD
const LAUNCH := Vector3i(2252, 4, 21)    # Launch Day: VY 0 began; each VY begins on 21 April

const DAYS3 := ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
const DAY_INDEX := {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
const DAY_NAMES := ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
const DAY_SHORT := ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const MONTH_NAMES := ["January", "February", "March", "April", "May", "June", "July", "August", "September",
	"October", "November", "December"]
const MONTH_SHORT := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

static var _start_jdn := -1
static var _cache := {}


# -- the day of the week ------------------------------------------------------------------------------------------

static func _load() -> void:
	if _loaded:
		return
	_loaded = true
	var ev = JSON.parse_string(FileAccess.get_file_as_string(EVENTS)) if FileAccess.file_exists(EVENTS) else null
	if not (ev is Dictionary):
		push_warning("StationCalendar: %s unreadable; the start is the bible's 2752-05-24, a Wednesday" % EVENTS)
		return
	var p := str(ev.get("start_date", "")).split("-")
	if p.size() == 3:
		_y = int(p[0])
		_m = int(p[1])
		_d = int(p[2])
	_wd = posmod(int(ev.get("start_weekday", START_WD)), 7)


static func start() -> Dictionary:
	## {y, m, d, wd} of game day 0.
	_load()
	return {"y": _y, "m": _m, "d": _d, "wd": _wd}


static func weekday(day: int) -> int:
	## 0 = Monday .. 6 = Sunday, of game day `day`.
	_load()
	return posmod(_wd + day, 7)


static func day_key(day: int) -> String:
	## "mon" .. "sun" (the schedules' and the places' hours' words).
	return DAYS3[weekday(day)]


static func is_weekend(day: int) -> bool:
	return weekday(day) >= 5


static func week(day: int) -> int:
	## Which week (Monday to Sunday) a game day falls in: the start's week is 0 (rotas turn over on Mondays).
	_load()
	return floori(float(day + _wd) / 7.0)


static func days_in_range(day: int, rule: String) -> bool:
	## "mon-fri", "fri-sun" (wraps past Sunday too: "sat-mon"), "daily", "never", a single "sat".
	match rule:
		"daily", "":
			return true
		"never":
			return false
	var p := rule.split("-")
	var wd := weekday(day)
	if p.size() == 1 and DAY_INDEX.has(p[0]):
		return wd == int(DAY_INDEX[p[0]])
	if p.size() == 2 and DAY_INDEX.has(p[0]) and DAY_INDEX.has(p[1]):
		var a := int(DAY_INDEX[p[0]])
		var b := int(DAY_INDEX[p[1]])
		return (wd >= a and wd <= b) if a <= b else (wd >= a or wd <= b)
	return true


# -- the date ---------------------------------------------------------------------------------------------------

static func date(day: int) -> Dictionary:
	## {y, m, d, wd (0 = Monday), vy, doy (1 = 1 January)} of a game day.
	if _cache.has(day):
		return _cache[day]
	var j := start_jdn() + day
	var out := from_jdn(j)
	out["wd"] = weekday(day)
	out["vy"] = vy_of(int(out.y), int(out.m), int(out.d))
	out["doy"] = j - jdn(int(out.y), 1, 1) + 1
	if _cache.size() > 256:
		_cache.clear()
	_cache[day] = out
	return out


static func day_of(y: int, m: int, d: int) -> int:
	## The game day of a date (negative before the start).
	return jdn(y, m, d) - start_jdn()


static func vy_of(y: int, m: int, d: int) -> int:
	## The Voyage Year: VY n runs from Launch Day (21 April) of 2252 + n.
	return y - LAUNCH.x - (1 if m * 100 + d < LAUNCH.y * 100 + LAUNCH.z else 0)


static func month_len(y: int, m: int) -> int:
	return jdn(y + (1 if m == 12 else 0), 1 if m == 12 else m + 1, 1) - jdn(y, m, 1)


static func in_season(day: int) -> bool:
	## The summer season (seasonal places: the ice-cream stands, the beach huts): May to September.
	var m := int(date(day).m)
	return m >= 5 and m <= 9


static func next_weekday(from_day: int, wd: int) -> int:
	## The first game day on or after from_day that is weekday wd.
	return from_day + posmod(wd - weekday(from_day), 7)


static func start_jdn() -> int:
	if _start_jdn < 0:
		_load()
		_start_jdn = jdn(_y, _m, _d)
	return _start_jdn


static func jdn(y: int, m: int, d: int) -> int:
	## The Julian day number of a Gregorian date.
	var a := (14 - m) / 12
	var yy := y + 4800 - a
	var mm := m + 12 * a - 3
	return d + (153 * mm + 2) / 5 + 365 * yy + yy / 4 - yy / 100 + yy / 400 - 32045


static func from_jdn(j: int) -> Dictionary:
	var a := j + 32044
	var b := (4 * a + 3) / 146097
	var c := a - 146097 * b / 4
	var d := (4 * c + 3) / 1461
	var e := c - 1461 * d / 4
	var m := (5 * e + 2) / 153
	return {"y": 100 * b + d - 4800 + m / 10, "m": m + 3 - 12 * (m / 10), "d": e - (153 * m + 2) / 5 + 1}


# -- words ------------------------------------------------------------------------------------------------------

static func format_date(day: int, long := true) -> String:
	## "Wednesday, 24 May 2752" (long) or "Wed 24 May" (short).
	var t := date(day)
	if long:
		return "%s, %d %s %d" % [DAY_NAMES[t.wd], t.d, MONTH_NAMES[int(t.m) - 1], t.y]
	return "%s %d %s" % [DAY_SHORT[t.wd], t.d, MONTH_SHORT[int(t.m) - 1]]


static func format_time(hour: float, twelve := true) -> String:
	## "9:05 AM" (or "09:05").
	var mins := posmod(int(floor(hour * 60.0 + 1e-4)), 1440)
	var h := mins / 60
	if not twelve:
		return "%02d:%02d" % [h, mins % 60]
	return "%d:%02d %s" % [12 if h % 12 == 0 else h % 12, mins % 60, "AM" if h < 12 else "PM"]
