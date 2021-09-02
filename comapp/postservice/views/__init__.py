from rest_framework.views import APIView
from rest_framework.response import Response
import time

from comlib.database import execute
import json
import pandas as pd



class CreatePost(APIView):
    """
    Create a post from the user.
    ---
    post_author_uuid: required String.
    post_name: required String.
    post_text: required String.
    post_url_slug: required String.
    post_scope: required List.
    post_media: required List.
    """
    def post(self, request):
        qp = request.query_params
        if 'post_author_uuid' not in qp:
            return Response({"error": True, "message": "post_author_uuid is a required parameter."}, status=403)
        #
        post_author_uuid = qp.get('post_author_uuid')
        # cols = [
        #     "post_name",
        #     "post_text",
        #     "post_url_slug",
        #     "post_scope",
        #     "post_media",
        # ]
        data_cols = []
        data_values = []
        if "post_name" in qp:
            data_cols.append('post_name')
            data_values.append(f" '{ qp.get('post_name') }' ")
        if "post_text" in qp:
            data_cols.append('post_text')
            data_values.append(f" '{ qp.get('post_text') }' ")
        if "post_url_slug" in qp:
            data_cols.append('post_url_slug')
            data_values.append(f" '{ qp.get('post_url_slug') }' ")
        if "post_scope" in qp:
            data_cols.append('post_scope')
            data_values.append(qp.get('post_scope'))
        if "post_media" in qp:
            data_cols.append('post_media')
            data_values.append(qp.get('post_media'))
        #
        query = f"""
        INSERT INTO comapp.posts (
            post_uuid, 
            post_timestamp,
            post_author_uuid,
            { ",".join(data_cols) },
            post_share_count, 
            post_comment_count, 
            post_reaction_count
        )
        VALUES (
            uuid(),
            toTimeStamp(now()), 
            '{post_author_uuid}',
            { ",".join(data_values) },
            0,
            0,
            0
        )
        """
        return_data = execute(query).all()
        return Response(return_data)

class PostDetails(APIView):
    """
    Return Props based on the following parameters.
    ---
    limit: optional int, limit query rows, 1000 default
    list: optional string, one of foreclosureDefault,
            defaults to foreclosureDefault.
    offset: optional int, offset to query, 0 default
    """

    def get(self, request):
        post_uuid = request.query_params.get('post_uuid', None)
        # post_author_uuid = request.query_params.get('post_author_uuid', None)
        if post_uuid is None :#and post_author_uuid is None:
            return Response({"error": True, "message": "post_uuid is a required parameters."}, status=403)
        q = f"""
        SELECT 
            *
        FROM 
            comapp.posts 
        WHERE 
            post_uuid={post_uuid}
        ;
        """
        return_data = execute(q).all()
        print(return_data)
        return Response(return_data)

class PostList(APIView):
    """
    Return List of Posts created by the specified user.
    ---
    author_uuid: required uuid.
    """

    def get(self, request):
        author_uuid = request.query_params.get('author_uuid', None)
        if author_uuid is None:
            return Response({"error": True, "message": "author_uuid is a required parameter."}, status=403)
        q = f"""
        SELECT 
            post_author_uuid, 
            post_uuid, 
            post_timestamp, 
            post_name, 
            post_text, 
            post_url_slug 
        FROM 
            comapp.posts 
        WHERE 
            post_author_uuid='{author_uuid}' 
        ORDER BY post_timestamp DESC;
        """
        return_data = execute(q).all()
        print(return_data)
        return Response(return_data)

class Analytics(APIView):
    """
    Return live Analytical data.
    """
    def get(self, request):
        return_data = self.get_data()
        print(return_data)
        return Response(return_data)

    @staticmethod
    def get_data():

        start = time.time()
        q = f"""
        SELECT 
            SUM(is_offensive) AS offensive,
            sum(is_age_restricted) AS age_restricted,
            sum(is_group_message) AS group_post,
            sum(is_global_message) AS global_post,
            sum(contains_media) AS contains_media 
        FROM 
            comapp.post_stats 
        WHERE
            post_timestamp >= toTimeStamp(NOW()) - 1h ALLOW FILTERING;
        """
        post_stats = execute(q).one()

        q = f"""
        SELECT
            post_author_uuid,
            COUNT(post_author_uuid) as ct
        FROM comapp.post_stats
        WHERE
            post_timestamp >= toTimeStamp(NOW()) - 1h
        GROUP BY
            post_author_uuid
        ALLOW FILTERING;
        """
        top_authors = execute(q).all()
        df = pd.DataFrame(top_authors).sort_values('ct', ascending=False).head(100).reset_index(drop=True).reset_index()
        df['index'] += 1
        top_authors = df.to_json(orient='records')
        top_authors = json.loads(top_authors)

        return_data = {
            "time_taken": time.time()-start,
            'post_stats': post_stats,
            'top_authors': top_authors
        }
        return return_data

from django.shortcuts import render

def analytics_view(request):
    data = Analytics.get_data()
    context = {'data': data}
    return render(request, 'index.html', context)
