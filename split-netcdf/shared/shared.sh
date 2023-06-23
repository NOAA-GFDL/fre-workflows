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
            format=%Y
            ;;
        6)
            format=%Y%m
            ;;
        8)
            format=%Y%m%d
            ;;
        10)
            format=%Y%m%d%H
            ;;
        12)
            format=%Y%m%d%H%M
            ;;
        *)
            echo "ERROR: unexpected date input '$1'"
            exit 1
            ;;
    esac

    isodatetime --print-format CCYYMMDDThhmm --parse-format $format $1
}

# Print suitable date template format given an frequency (ISO 8601 duration)
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
            # NOTE: isodatetime doesn't accept CCYYMMDDhh, so the T must be removed later
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
    isodatetime --print-format $format $1 | tr -d T
}
