USAGE = """{bold}{appname}{clear}\n\tRESIF data transfer - send data to RESIF datacentre, or get logs from the datacentre\n
{bold}VERSION{clear}\n\t{version}\n
{bold}SYNOPSIS{clear}\n\t{prog} [-h|--help] [-t|--test] [-c|--config CONFIG_FILE] [-s|--send DIRECTORY -d|--datatype TYPE] [-r|--retrieve-logs TRANSACTION_ID]\n
{bold}DESCRIPTION{clear}
\t{bold}-h, --help{clear}\t\tshows this help
\t{bold}-t, --test{clear}\t\tperforms a test (no transfer done)
\t{bold}-c, --config{clear}\t\tuse alternate configuration file (see CONFIG FILE section)
\t{bold}-s, --send{clear}\t\tsend whole DIRECTORY content to remote datacentre (see SENDING DATA and TRANSACTION sections)
\t{bold}-d, --data-type{clear}\t\ttype of data being held into DIRECTORY (see -s and DATA TYPE section)
\t{bold}-r, --retrieve-logs{clear}\tretrieve transaction logs (see TRANSACTION section). Outputs on stdout.
\t{bold}-i, --ignore-limits{clear}\tignore limits (see [limits] in configuration file)

\tNote : {bold}-s{clear} implies {bold}-d{clear}, {bold}-s{clear} and {bold}-r{clear} are mutually exclusive.

{bold}DEFAULT CONFIGURATION FILE{clear}\n\t{config}

{bold}SENDING DATA{clear}
\tThe {bold}-s{clear} option allows sending a whole directory content to the remote datacentre.
\tWhen using -s, one must also specify the data type being sent with -d.
\tAfter transfer is succedded, a transaction identifier is generated and [FIXME]

{bold}DATA TYPE{clear}
\tTells what kind of data are being sent to the remote datacentre :
\t\t{bold}seismic_data{clear}\tvalidated seismic data
\t\t{bold}seismic_metadata{clear}\tvalidated seismic metadata [FIXME]

{bold}TRANSACTION{clear}\n\t[FIXME]

{bold}REQUIREMENTS{clear}\n\t
\tWorks with Python version between {vmin} and {vmax}. Needs rsync and du commands.

{bold}SUPPORT{clear}\n\t{contact}

{bold}SEE ALSO{clear}\n\t[FIXME]

This is BETA version. Do not use for production.
"""
