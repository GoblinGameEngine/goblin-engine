extends RefCounted
class_name DataFile

## The game's big data files, plain or gzipped (the size plan's compressed JSON, research/buildings/kit_design.md).
##
## In the project a file is its plain self (res://remake/placement.json); tools/pack_data.py writes a gzipped twin
## beside it (placement.json.gz) and the exported game ships only the twin (export_presets.cfg).  Readers ask here and
## get the same text either way:
##
##   DataFile.exists(p)    p or p.gz is there
##   DataFile.text(p)      the file's text (from p, else p.gz)
##   DataFile.get_var(p)   a FileAccess.store_var() file's value (the .bin bakes: placement, terrain, lives ...)
##   DataFile.md5(p)       the MD5 of the plain file's bytes, from either -- so bake fingerprints (BakedMeshes) match in
##                         the project and in the game

static var _md5 := {}
static var _mx := Mutex.new()


static func exists(p: String) -> bool:
	return FileAccess.file_exists(p) or FileAccess.file_exists(p + ".gz")


static func bytes(p: String) -> PackedByteArray:
	if FileAccess.file_exists(p):
		return FileAccess.get_file_as_bytes(p)
	if FileAccess.file_exists(p + ".gz"):
		return FileAccess.get_file_as_bytes(p + ".gz").decompress_dynamic(-1, FileAccess.COMPRESSION_GZIP)
	return PackedByteArray()


static func text(p: String) -> String:
	if FileAccess.file_exists(p):
		return FileAccess.get_file_as_string(p)
	return bytes(p).get_string_from_utf8()


static func get_var(p: String) -> Variant:
	if FileAccess.file_exists(p):
		var f := FileAccess.open(p, FileAccess.READ)
		var v = f.get_var()
		f.close()
		return v
	var b := bytes(p)
	return bytes_to_var(b.slice(4)) if b.size() > 4 else null      # (store_var: a 32-bit length, then the value)


static func json(p: String):
	## the parsed file (null: none)
	return JSON.parse_string(text(p)) if exists(p) else null


static func md5(p: String) -> String:
	if FileAccess.file_exists(p):
		return FileAccess.get_md5(p)
	if not FileAccess.file_exists(p + ".gz"):
		return ""
	_mx.lock()
	var m: String = _md5.get(p, "")
	_mx.unlock()
	if m == "":
		var ctx := HashingContext.new()
		ctx.start(HashingContext.HASH_MD5)
		ctx.update(bytes(p))
		m = ctx.finish().hex_encode()
		_mx.lock()
		_md5[p] = m
		_mx.unlock()
	return m
