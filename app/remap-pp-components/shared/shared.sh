# Fancy print to standard error
err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

# Parse a date string
# Accepts date in YYYYMMDDHHmm or less precision
# Outputs date in standard ISO8601 (YYYYMMDDTHHmm) format
function parse_date {
    case ${#1} in
        4)
            input=$1
            ;;
        6)
            input=${1}01
            ;;
        8)
            input=$1
            ;;
        10)
            input=$(echo $1 | sed 's/\(..\)$/T\1/')
            ;;
        12)
            input=$(echo $1 | sed 's/\(....\)$/T\1/')
            ;;
        *)
            echo "ERROR: unexpected date input '$1'"
            exit 1
            ;;
    esac

    cylc cycle-point --template CCYYMMDDThhmm $input
}

# Print legacy Bronx-like date template format given an frequency (ISO 8601 duration)
function freq_to_date_format {
    case $1 in
        P1Y)
            echo CCYY
            ;;
        P1M)
            echo CCYYMM
            ;;
        P1D)
            echo CCYYMMDD
            ;;
        PT*H)
            # NOTE: cylc date --format doesn't accept CCYYMMDDhh, so the T must be removed later
            echo CCYYMMDDThh
            ;;
        *)
            echo ERROR: Unknown frequency $1
            exit 1
            ;;
    esac
}

# Print a date string to a truncated precision
# Accepts a date and frequency
# Outputs a date string with suitably reduced precision
function truncate_date {
    format=$(freq_to_date_format $2)
    cylc cycle-point --template $format $1 | tr -d T
}

# Determine frequency based on two days
# Outputs two strings: frequency and associated format (used by isodatetime)
function get_freq_and_format_from_two_days {
    hours=$(echo "($1+$2)*24" | bc)
    get_freq_and_format_from_hours $hours
}

# Determine frequency based on two dates
# Outputs two strings: frequency and associated format (used by isodatetime)
function get_freq_and_format_from_two_dates {
    hours=$(isodatetime --calendar=365day --as-total=H $1 $2)
    hours=${hours%.0}
    get_freq_and_format_from_hours $hours
}

# Determine frequency based on hours
# Outputs two strings: frequency and associated foramt (used by isodatetime)
function get_freq_and_format_from_hours {
    hours=$1

    #floor of user input- keep everything to left of decimal (if present)
    hoursfl=${hours%%.*}

    #if floor and input not equal, there was a decimal. 
    if [[ $hoursfl != $hours ]]; then
	#grab the remainder of input
	hoursrem=${hours##*.}

	#trim zeroes from right of decimal, if present
	hoursrem=${hoursrem%%0*}
    else
	hoursrem=-1
    fi

    # annual (this is so questionable)
    if (( hoursfl > 4320 )); then
        freq=P1Y
        format=CCYY
    # monthly
    elif (( hoursfl > 671 && hoursfl < 745 )); then
        freq=P1M
        format=CCYYMM
    # daily
    elif (( hoursfl == 24 )); then
        freq=P1D
        format=CCYYMMDD
    # hourly
    elif (( hoursfl < 24 && hoursfl != 0 )); then
        freq=PT${hoursfl}H
        # arrgg, isodatetime doesn't accept CCYYMMDDhh
        format=CCYYMMDDThh
    # subhourly
    elif (( hoursfl == 0 && hoursrem > 0 )); then
	freq=PT0.${hoursrem}H
        # arrgg, isodatetime doesn't accept CCYYMMDDhh
        format=CCYYMMDDThh
    else
        err ERROR: Could not determine frequency for hours=$hours
        # Not sure if exiting 1 is better or something else. (python, in any case)
        #exit 1
        freq=error
        format=error
    fi

    echo "$freq $format"
}


# Print Bronx-style frequency given an ISO8601 duration
function freq_to_legacy {
    case $1 in
        P1Y)
            echo annual
            ;;
        P1M)
            echo monthly
            ;;
        P3M)
            echo seasonal
            ;;
        P1D)
            echo daily
            ;;
        PT120H)
            echo 120hr
            ;;
        PT12H)
            echo 12hr
            ;;
        PT8H)
            echo 8hr
            ;;
        PT6H)
            echo 6hr
            ;;
        PT4H)
            echo 4hr
            ;;
        PT3H)
            echo 3hr
            ;;
        PT2H)
            echo 2hr
            ;;
        PT1H)
            echo hourly
            ;;
        PT30M)
            echo 30min
            ;;
        *)
            echo ERROR: Unknown frequency $1
            exit 1
            ;;
    esac
}

# Print Bronx-style frequency given an ISO8601 duration
function chunk_to_legacy {
    if [[ $1 =~ ^P([0-9]+)Y$ ]]; then
        echo ${BASH_REMATCH[1]}yr
    elif [[ $1 =~ ^P([0-9])+M$ ]]; then
        echo ${BASH_REMATCH[1]}mo
    else
        err ERROR: Unknown chunk $1
        # want to return error code here
        echo error
    fi
}
