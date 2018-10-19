import os
from confapp import conf
from send2trash import send2trash
from pythonvideoannotator_models.utils import tools
from pythonvideoannotator.utils.tools import list_files_in_path

class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self._update_time = True  # Use to avoid double video jump 2 frame trigger

		self.mainmenu[2]['Windows'].append({'Timeline': self.__show_timeline_event, 'icon':conf.PYFORMS_ICON_EVENTTIMELINE_TIMELINE })
		



	def __show_timeline_event(self):
		self._dock.show()

	def init_form(self):
		self._time.pointer_changed_event = self.__time_changed
		#self._time.isPlaying      = self.__timeline_play_video
		#self._time.fpsChanged     = self.__timeline_fps_changed
		#self._time.getExportFilename= self.__createFilename2Export
		super(Module, self).init_form()

	######################################################################################
	#### HELPERS #########################################################################
	######################################################################################

	def __createFilename2Export(self, nameformat="%s_events.csv"):
		if self._filename.value == '': return 'untitled.csv'
		filepath = os.path.dirname(self._filename.value)
		filename = os.path.basename(self._filename.value)
		name, ext = os.path.splitext(filename)
		return os.path.join(filepath, nameformat % name)

	######################################################################################
	#### EVENTS ##########################################################################
	######################################################################################

	def __time_changed(self):
		"""
		If the timeline pointer is changed the player position is also changed
		"""
		if self._player.value is None: return

		# Flag to avoid recursive position change, between the player and the timeline
		self._update_time = False        
		self._player.video_index = self._time.value-1
		self._player.update_frame()
		self._update_time = True

	def __dummy(self): pass

	def __timeline_play_video(self):
		"""
		Function called when the Play/Pause control is issued from
		the timeline.
		"""
		if self._time._time._video_playing:
			timeout_interval = (1000 / self._player.fps)
			self._player._timer.start(timeout_interval)
		else:
			self._player._timer.stop()

	def __timeline_fps_changed(self):
		"""Function called when the FPS rate is changed by the timeline."""
		self._player._form.videoFPS.setValue(self._time._time.fps)
		self._player.videoFPS_valueChanged()

	def process_frame_event(self, frame):
		if self._update_time and self._player.value:
			self._time.pointer_changed_event = self.__dummy
			self._time.value = self._player.video_index-1
			self._time.pointer_changed_event = self.__time_changed
				
		return super(Module, self).process_frame_event(frame)



	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	
	def save(self, data, project_path=None):
		data = super(Module,self).save(data, project_path)
		graphs_path = os.path.join(project_path, 'graphs')
		if not os.path.exists(graphs_path): os.makedirs(graphs_path)

		graphs = []
		for graph in self._time.graphs:
			graph_path = os.path.join(graphs_path, graph.name+'.csv')
			graph.export_2_file(graph_path)
			graphs.append(graph_path)


		for path in tools.list_files_in_path(graphs_path):
			if path not in graphs: send2trash(path)

		return data

	def load(self, data, project_path=None):
		graphs_path = os.path.join(project_path, 'graphs')
		for graph_path in list_files_in_path(graphs_path):
			self._time.import_graph_file(graph_path, ignore_rows=1)
		
		super(Module,self).load(data, project_path)
		
