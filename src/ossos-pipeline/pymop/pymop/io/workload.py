__author__ = "David Rusk <drusk@uvic.ca>"

import os

from pymop import tasks


class NoAvailableWorkException(Exception):
    """"No more work is available."""


class WorkItem(object):
    """
    An individual piece of work.
    """

    def __init__(self, filename, working_directory, progress_manager):
        self.filename = filename
        self.working_directory = working_directory
        self.progress_manager = progress_manager
        self.finished = False

    def get_filename(self):
        return self.filename

    def get_full_path(self):
        return os.path.join(self.working_directory, self.filename)

    def set_finished(self):
        self.finished = True


class Workload(object):
    """
    A collection of related WorkItems.
    """

    def __init__(self, astrom_data):
        self.astrom_data = astrom_data

    def set_finished(self):
        pass


class RealsWorkload(object):
    """
    """

    def __init__(self, astrom_data):
        super(RealsWorkload, self).__init__(astrom_data)


class CandidatesWorkload(object):
    """
    """

    def __init__(self, astrom_data):
        super(CandidatesWorkload, self).__init__(astrom_data)


class WorkloadFactory(object):
    """
    Creates WorkItems.
    """

    def __init__(self, working_directory, progress_manager, parser):
        self.working_directory = working_directory
        self.progress_manager = progress_manager
        self.parser = parser

    def create_workload(self):
        potential_files = self._list_potential_files()

        while len(potential_files) > 0:
            potential_file = potential_files.pop()

            if not self.progress_manager.is_done(potential_file):
                return self._create_workload(
                    self.parser.parse(
                        os.path.join(self.working_directory, potential_file)))

        raise NoAvailableWorkException()

    def _create_workload(self, data):
        raise NotImplementedError()

    def _list_potential_files(self):
        raise NotImplementedError()


class RealsWorkloadFactory(WorkloadFactory):
    """
    Creates WorkItems for the processing reals task.
    """

    def __init__(self, working_directory, progress_manager):
        super(RealsWorkloadFactory, self).__init__(
            working_directory, progress_manager)

    def _create_workload(self, data):
        return RealsWorkload(data)

    def _list_potential_files(self):
        return tasks.listdir_for_task(self.working_directory, tasks.REALS_TASK)


class CandidatesWorkloadFactory(WorkloadFactory):
    """
    Creates WorkItems for the processing candidates task.
    """

    def __init__(self, working_directory, progress_manager):
        super(RealsWorkloadFactory, self).__init__(
            working_directory, progress_manager)

    def _create_workload(self, data):
        return CandidatesWorkload(data)

    def _list_potential_files(self):
        return tasks.listdir_for_task(self.working_directory, tasks.CANDS_TASK)


class WorkloadManager(object):
    """
    Manages the workload's state.
    """

    def __init__(self, workload_factory):
        self.workload_factory = workload_factory
        self.current_workload = None
        self.workload_number = 0
