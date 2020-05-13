import shotgun_api3


class shotgun:
    def __init__(self, hostname, login, password):
        self.hostname = hostname
        self.login = login
        self.password = password
        self.sg = shotgun_api3.Shotgun(self.hostname, login=self.login, password=self.password)

    def get_project(self, project_name):
        project = self.sg.find_one('Project',  [['name', 'is', project_name]], ['id', 'name'])
        if project:
            return project
        else:
            print('Could not find {0} Project in SG'.format(project_name))
            return None

    def create_project(self, project_name):
        data = {
            'name': project_name,
        }
        return self.sg.create('Project', data)

    def get_sequence(self, project, seq_name):
        sFilters = [['project', 'is', project], ['code', 'is', seq_name]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Sequence', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Sequence in SG'.format(seq_name))
        return None

    def create_seq(self, project, seq_name):
        data = {
            'project': {"type": "Project", "id": project['id']},
            'code': seq_name,
            'sg_status_list': "ip"
        }
        return self.sg.create('Sequence', data)

    def get_shot(self, project, seq, shot_name):
        sFilters = [['project', 'is', project], ['sg_sequence', 'is', seq], ['code', 'is', shot_name]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Shot', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Shot in SG'.format(shot_name))
        return None

    def create_shot(self, project, seq, shot_name):
        data = {
            "project": {"type": "Project", "id": project['id']},
            'code': shot_name,
            'sg_sequence': {'type': 'Sequence', 'id': seq['id']},
            'sg_status_list': 'ip'
        }
        return self.sg.create('Shot', data)

    def get_version(self, project, shot):
        sFilters = [['project', 'is', project], ['entity', 'is', {'type': 'Shot', 'id': shot['id']}]]
        sFields = ['id', 'code']
        sgSeq = self.sg.find_one('Version', sFilters, sFields)
        if sgSeq:
            return sgSeq
        else:
            print('Could not find {0} Version in SG'.format(shot['code']))
        return None

    def create_version(self, show, shot, version_number):
        data = {'project': {'type': 'Project', 'id': show['id']},
                'code': shot['code'] + "_v%03d" % version_number,
                'sg_status_list': 'rev',
                'entity': {'type': 'Shot', 'id': shot['id']}
                }
        return self.sg.create('Version', data)

    def upload_movie(self, version, movie_path):
        return self.sg.upload('Version', version['id'], movie_path, field_name='sg_uploaded_movie')
