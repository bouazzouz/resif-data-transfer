USAGE = """{bold}{appname}{clear}\n\tRESIF data transfer - send data to RESIF datacentre, get transaction logs from the datacentre\n
{bold}VERSION{clear}\n\t{version}\n
{bold}SYNOPSIS{clear}\n\t{prog} [-h|--help] [-t|--test] [-c|--config CONFIG_FILE] [-s|--send DIRECTORY -d|--datatype TYPE] [-r|--retrieve-logs TRANSACTION_ID]\n
{bold}DESCRIPTION{clear}
\t{bold}-h, --help{clear}\t\tshows this help
\t{bold}-t, --test{clear}\t\tperforms a test (no transfer done)
\t{bold}-c, --config{clear}\t\tuse alternate configuration file
\t{bold}-s, --send{clear}\t\tsend whole DIRECTORY content to remote datacentre (see SENDING DATA)
\t{bold}-d, --data-type{clear}\t\ttype of data being held into DIRECTORY (see -s and DATA TYPE section)
\t{bold}-r, --retrieve-logs{clear}\tretrieve transaction logs (see TRANSACTION STATUS)
\t{bold}-i, --ignore-limits{clear}\tignore limits (see [limits] in configuration file)

\tNote : {bold}-s{clear} implies {bold}-d{clear}, {bold}-s{clear} and {bold}-r{clear} are mutually exclusive.

{bold}DEFAULT CONFIGURATION FILE{clear}\n\t{config}

{bold}SENDING DATA{clear}
\tThe {bold}-s{clear} option allows sending a whole directory content to the remote datacentre.
\tWhen using -s, one must also specify the data type being sent with -d.
\tAfter transfer is succedeed, logbook file is updated 
\tand a unique transaction identifier is printed on stdout.
\tIf {bold}-t{clear} flag is on, no effective transfer will be done (useful for testing/debugging).

{bold}DATA TYPES{clear}
\tTells what kind of data is being sent to the remote datacentre :
\t\t{bold}seismic_data{clear}\t\tvalidated seismic data
\t\t{bold}seismic_metadata{clear}\tvalidated seismic metadata

{bold}TRANSACTION STATUS{clear}
\tThe {bold}-r{clear} option allows retrieving status information (XML formatted) for a given transaction identifier. Status is printed on stdout.

{bold}RETURN VALUES{clear}
\tReturns 0 on success. 
\tSome short error messages may be printed on stderr, see also configuration file for log files.

{bold}EXAMPLE USAGES{clear}
\tFIXME. 

{bold}REQUIREMENTS & SUPPORT{clear}
\tWorks with Python version between {vmin} and {vmax}. Needs 'rsync' and 'du' commands (or any compatible command). 
\tThis is a test version : do not use for production.
""" 
