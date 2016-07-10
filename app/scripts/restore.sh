echo "**************************************"
echo "Beginning restore of the database"
echo "This should be fun..."
echo "**************************************"

LOGLEVEL=0

# make a copy of the database with a time stamp
# store in the raw_data dir
STAMP=$(date "+%Y-%m-%d")
cp db.sqlite3 raw_data/${STAMP}.sqlite3
rm db.sqlite3

# run the init of the db
echo "**************************************"
echo "Running django table migrations"
echo "**************************************"
python manage.py migrate auth -v $LOGLEVEL
python manage.py migrate sessions -v $LOGLEVEL
python manage.py migrate contenttypes -v $LOGLEVEL
python manage.py migrate admin -v $LOGLEVEL

echo "**************************************"
echo "Running history as of 7/10/2016"
echo "**************************************"
# walk through history
python manage.py migrate games 0016 -v $LOGLEVEL
echo "**************************************"
echo "Populating team table..."
echo "**************************************"
python manage.py populate_team_table
echo "**************************************"
echo "Populating stadium table..."
echo "**************************************"
python manage.py populate_stadium_table
echo "**************************************"
echo "Populating game table..."
echo "**************************************"
python manage.py populate_game_table -v $LOGLEVEL
python manage.py migrate events 0001 -v $LOGLEVEL

echo "**************************************"
echo "Cleaning things up"
echo "**************************************"
# run up
python manage.py migrate -v $LOGLEVEL
echo "**************************************"
echo "SUCCESS!!!!"
echo "The old database is backed up in the "
echo "raw_data/ directory under "${STAMP}
echo "The new one is ready to go."
echo "**************************************"
