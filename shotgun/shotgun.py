from typing import Dict

import shotgun_api3


class shotgun:
    """shotgun will handle the login and expose functions to get, create
    projects etc."""

    def __init__(self, hostname: str, login: str, password: str):
        self.hostname = hostname
        self.login = login
        self.password = password
        self.sg = shotgun_api3.Shotgun(self.hostname,
                                       login=self.login,
                                       password=self.password)

    def get_project(self, project_name: str) -> Dict:
        """get_project will try to retrieve a project by name.

        Arguments:
            project_name {str} -- Name of the project to retrieve

        Returns:
            Dict -- Project from Shotgun
        """
        project = self.sg.find_one('Project',
                                   [['name', 'is', project_name]],
                                   ['id', 'name'])
        if project:
            return project
        print('Could not find {0} Project in SG'.format(project_name))
        return None

    def create_project(self, project_name: str) -> Dict:
        """create_project will create a project.

        Arguments:
            project_name {str} -- Project name

        Returns:
            Dict -- Project from Shotgun
        """
        data = {
            'name': project_name,
        }
        return self.sg.create('Project', data)

    def get_sequence(self, project: Dict, seq_name: str) -> Dict:
        """get_sequence will retrieve a sequence.

        Arguments:
            project {Dict} -- Project from Shotgun

            seq_name {str} -- Sequence name

        Returns:
            Dict -- Sequence from Shotgun
        """
        sFilters = [['project', 'is', project], ['code', 'is', seq_name]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Sequence', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Sequence in SG'.format(seq_name))
        return None

    def create_seq(self, project: Dict, seq_name: str) -> Dict:
        """create_seq will create a sequence.

        Arguments:
            project {Dict} -- Project from Shotgun

            seq_name {str} -- Sequence name

        Returns:
            Dict -- Sequence from Shotgun
        """
        data = {
            'project': {"type": "Project", "id": project['id']},
            'code': seq_name,
            'sg_status_list': "ip"
        }
        return self.sg.create('Sequence', data)

    def get_shot(self, project: Dict, seq: Dict, shot_name: str) -> Dict:
        """get_shot will retrieve a shot from Shotgun.

        Arguments:
            project {Dict} -- Project from Shotgun

            seq {Dict} -- Sequence from Shotgun

            shot_name {str} -- Shot name

        Returns:
            Dict -- Shot from Shotgun
        """
        sFilters = [
            ['project', 'is', project],
            ['sg_sequence', 'is', seq],
            ['code', 'is', shot_name]
        ]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Shot', sFilters, sFields)
        if sgSeq:
            return sgSeq
        print('Could not find {0} Shot in SG'.format(shot_name))
        return None

    def create_shot(self, project: Dict, seq: Dict, shot_name: str) -> Dict:
        """create_shot will create a shot.

        Arguments:
            project {Dict} -- Project from Shotgun

            seq {Dict} -- Sequence from Shotgun

            shot_name {str} -- Shot name

        Returns:
            Dict -- Shot from Shotgun
        """
        data = {
            "project": {"type": "Project", "id": project['id']},
            'code': shot_name,
            'sg_sequence': {'type': 'Sequence', 'id': seq['id']},
            'sg_status_list': 'ip'
        }
        return self.sg.create('Shot', data)

    def get_version(self, project: Dict, shot: Dict) -> Dict:
        """get_version will retrieve a version.

        Arguments:
            project {Dict} -- Project from Shotgun

            shot {Dict} -- Shot from Shotgun

        Returns:
            Dict -- Version from Shotgun
        """
        sFilters = [
            ['project', 'is', project],
            ['entity', 'is', {'type': 'Shot', 'id': shot['id']}]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Version', sFilters, sFields)
        if sgSeq:
            return sgSeq
        print('Could not find {0} Version in SG'.format(shot['code']))
        return None

    def create_version(
            self, project: Dict, shot: Dict, version_nbr: int) -> Dict:
        """create_version will create a version.

        Arguments:
            project {Dict} -- Project from Shotgun

            shot {Dict} -- Shot from Shotgun

            version_nbr {int} -- Version number

        Returns:
            Dict -- Version from Shotgun
        """
        data = {'project': {'type': 'Project', 'id': project['id']},
                'code': shot['code'] + "_v%03d" % version_nbr,
                'sg_status_list': 'rev',
                'entity': {'type': 'Shot', 'id': shot['id']}
                }
        return self.sg.create('Version', data)

    def upload_movie(self, version: Dict, movie_path: str) -> Dict:
        """upload_movie will upload a movie to Shotgun.

        Arguments:
            version {Dict} -- Version from Shotgun

            movie_path {str} -- Movie path to upload

        Returns:
            Dict -- Movie upload from Shotgun
        """
        return self.sg.upload('Version', version['id'],
                              movie_path, field_name='sg_uploaded_movie')
