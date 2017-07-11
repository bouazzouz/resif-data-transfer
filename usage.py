USAGE = """{bold}{appname}{clear}\n\tSends data to RESIF datacentre, gets transaction logs from the datacentre\n
{bold}VERSION{clear}\n\t{version}\n
{bold}SYNOPSIS{clear}\n\t{prog} [-h|--help] [-t|--test] [-c|--config CONFIG_FILE] [-s|--send DIRECTORY -d|--datatype TYPE] [-r|--retrieve-logs TRANSACTION_ID] [-l|--logbook] [-b|--debug]\n
{bold}DESCRIPTION{clear}

\t{bold}-h, --help{clear}\t\tshows this help
\t{bold}-t, --test{clear}\t\tperforms a test (no file transfer done)
\t{bold}-c, --config{clear}\t\tuse alternate configuration file
\t{bold}-s, --send{clear}\t\tsend whole DIRECTORY content to remote datacentre (see SENDING DATA)
\t{bold}-d, --data-type{clear}\t\ttype of data being held into DIRECTORY (see -s and DATA TYPE section)
\t{bold}-r, --retrieve-logs{clear}\tretrieve transaction logs (see TRANSACTION STATUS)
\t{bold}-i, --ignore-limits{clear}\tignore limits (see [limits] in configuration file)
\t{bold}-l, --logbook{clear}\t\tdump logbook to stdout (see LOGBOOK)
\t{bold}-v, --version{clear}\t\tprint version and exit

\tNote : {bold}-s{clear} implies {bold}-d{clear}, {bold}-s{clear} {bold}-r{clear} and {bold}-l{clear} are mutually exclusive.

{bold}DEFAULT CONFIGURATION FILE{clear}

{config}

{bold}SENDING DATA{clear}

The {bold}-s{clear} option allows sending a whole directory content to the remote datacentre. When using -s, one must also specify the data type being sent with -d. After transfer is succedeed, logbook file is updated and a unique transaction identifier is printed on stdout. If {bold}-t{clear} flag is on, no effective transfer will be done (useful for testing/debugging).

{bold}DATA TYPES{clear}

Tells what kind of data is being sent to the remote datacentre :
\t{bold}seismic_data_miniseed{clear}\t\tvalidated seismic data (miniseed format)
\t{bold}seismic_metadata_dataless_seed{clear}\tvalidated seismic metadata (dataless seed format)

{bold}TRANSACTION STATUS{clear}

The {bold}-r{clear} option allows retrieving status information (XML formatted) for a given transaction identifier. Status is printed on stdout.
XML content is described into main documentation.

{bold}LOGBOOK{clear}

The logbook file keeps track of the transfers you made to the datacentre.  It is also used to compute the maximum volume of data you are expected to push to the datacentre within a given time window (see also {bold}-i{clear}). This file is JSON-formatted. You may dump it on stdout using the {bold}-l{clear} flag, colums are : transaction identifier, date, node name, data type, source directory, size (rounded as Gb).

{bold}RETURN VALUES{clear}

Returns 0 on success. Some error messages may be printed on stderr, see also configuration file for log files.

{bold}EXAMPLE USAGES{clear}

Test sending a directory with seismic data (remove {bold}-t{clear} to perform real sending) :
$ ResifDataTransfer.py -s /my/data/2011/January/ -d seismic_data_miniseed -t

Retrieve a transaction status, pretty print with xmllint :
$ ResifDataTransfer.py -r XMV1374 | xmllint --format -
 
Use an alternate configuration file :
$ ResifDataTransfer.py -c /etc/mytransfer.conf (...)

""" 
