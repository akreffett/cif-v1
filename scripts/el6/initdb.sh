#!/bin/bash
# Initialize the CIF data base. This script performs the same steps as libcif-dbi's make initdb performs.

# Change these to match your environment
PSQL=${PSQL:-/usr/bin/psql}
CHCON=${CHCON:-/usr/bin/chcon}
DB_SCHEMAS=${DB_SCHEMAS:-../schemas}
DB_DBA=${DB_DBA:-postgres}
DB_DATABASE=${DB_DATABASE:-cif}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_ARCHIVE_LOC=${DB_ARCHIVE_LOC:-/mnt/archive/data}
DB_INDEX_LOC=${DB_INDEX_LOC:-/mnt/index/data}
DB_ARCHIVE_TS=${DB_ARCHIVE_TS:-archive}
DB_INDEX_TS=${DB_INDEX_TS:-index}
DB_UNIXOWNER=${DB_UNIXOWNER:-postgres}
DB_SELINUX_CTX=${DB_SELINUX_CTX:-postgresql_db_t}
DB_TYPE=${DB_TYPE:-Pg}

initdb() {
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -c "CREATE DATABASE $DB_DATABASE"
	if [ ! -d "$DB_ARCHIVE_LOC" ] ; then
		mkdir -p "$DB_ARCHIVE_LOC" && chown "$DB_UNIXOWNER":"$DB_UNIXOWNER" "$DB_ARCHIVE_LOC"
		[ -x "$CHCON" ] && $CHCON -t "$DB_SELINUX_CTX" "$DB_ARCHIVE_LOC"
	fi
        $PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_DATABASE" -c "CREATE TABLESPACE $DB_ARCHIVE_TS LOCATION '$DB_ARCHIVE_LOC'"
	if [ ! -d "$DB_INDEX_LOC" ] ; then
                mkdir -p "$DB_INDEX_LOC" && chown "$DB_UNIXOWNER":"$DB_UNIXOWNER" "$DB_INDEX_LOC"
                [ -x "$CHCON" ] && $CHCON -t "$DB_SELINUX_CTX" "$DB_INDEX_LOC"
        fi
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_DATABASE" -c "CREATE TABLESPACE $DB_INDEX_TS LOCATION '$DB_INDEX_LOC'"
}

tables() {
	find "$DB_SCHEMAS/$DB_TYPE" -type f -print | grep -v index | sort | while read file ; do
    		$PSQL -U "$DB_DBA" -d "$DB_DATABASE" -h "$DB_HOST" -p "$DB_PORT" < "$file" 
    	done
	echo Tables built
	find "$DB_SCHEMAS/$DB_TYPE/index" -type f -print | sort | while read file ; do
                $PSQL -U "$DB_DBA" -d "$DB_DATABASE" -h "$DB_HOST" -p "$DB_PORT" < "$file"          
        done
	echo Indices built
}

dropdb() {
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -c "DROP DATABASE IF EXISTS $DB_DATABASE"
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -c "DROP TABLESPACE IF EXISTS $DB_ARCHIVE_TS"
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -c "DROP TABLESPACE IF EXISTS $DB_INDEX_TS"
}

purgedb() {
	$PSQL -U "$DB_DBA" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_DATABASE" < "$DB_SCHEMAS/pg_purge.sql"
}

case "$1" in
	"")
	initdb
	tables
	;;

	initdb)
	initdb
	;;

	tables)
	tables
	;;

	dropdb)
	dropdb
	;;

	purgedb)
	purgedb
	;;

	*)
	echo Usage: 'initdb.sh [tables|dropdb|purgedb]'
	exit 1
	;;
esac

exit $?
