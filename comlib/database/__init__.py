from cassandra.cluster import Cluster
from cassandra import InvalidRequest
from cassandra.cluster import NoHostAvailable
from cassandra.query import dict_factory

cluster_configs = {
    "default": {}
}

cluster_sessions = {}

def create_session(
        cluster_name="default",
        keyspace='comapp'
):
    global cluster_configs
    cluster = Cluster(**cluster_configs.get(cluster_name, {}))
    try:
        session = cluster.connect(keyspace)
    except (InvalidRequest, NoHostAvailable):
        pass
        session = cluster.connect()
        q = f"CREATE KEYSPACE {keyspace}"+" WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};"
        print(q)
        session.execute(q)
        session.set_keyspace(keyspace)
    #
    session.row_factory = dict_factory
    return session

def create_tables(
        cluster_name="default",
        keyspace='comapp'
):
    session = get_session(cluster_name, keyspace)
    # Create Posts Table
    session.execute(f"""
    CREATE TABLE {keyspace}.posts (
        post_author_uuid VARCHAR,
        post_uuid uuid,
        post_timestamp timestamp,
        post_name VARCHAR,
        post_text VARCHAR,
        post_url_slug VARCHAR,
        post_scope LIST<TEXT>,
        post_media LIST<FROZEN<MAP<TEXT, TEXT>>>,
        post_share_count INT,
        post_comment_count INT,
        post_reaction_count INT,
        post_comments LIST<FROZEN<MAP<TEXT, TEXT>>>,
        post_reactions LIST<FROZEN<MAP<TEXT, TEXT>>>,
        PRIMARY KEY ((post_author_uuid), post_timestamp)
    );
    """)
    session.execute(f"CREATE INDEX post_uuid_idx ON {keyspace}.posts ( post_uuid );")

def get_session(
        cluster_name="default",
        keyspace='comapp'
):
    global cluster_sessions
    if cluster_sessions.get(cluster_name, {}).get(keyspace, None) is not None:
        session = cluster_sessions.get(cluster_name).get(keyspace)
        try:
            output = session.execute("Describe TABLES;").one()
            return session
        except InvalidRequest:
            pass
    #
    session = create_session(cluster_name, keyspace)
    if cluster_name in cluster_sessions:
        cluster_sessions[cluster_name] = {
            keyspace: session
        }
    else:
        cluster_sessions = {
            cluster_name: {
                keyspace: session
            }
        }
    return session

def execute(
        query,
        cluster_name="default",
        keyspace='comapp',
        session=None
):
    if session is None:
        session = get_session(cluster_name, keyspace)
    return session.execute(query)

def flush_database_dev(
        cluster_name="default",
        keyspace='comapp',
        session=None
):
    if session is None:
        session = get_session(cluster_name, keyspace)
    session.execute(f"Drop Keyspace {keyspace};")
    create_tables()


