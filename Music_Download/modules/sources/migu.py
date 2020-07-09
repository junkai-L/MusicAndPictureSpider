'''
Function:
	咪咕音乐下载: http://www.migu.cn/
Author:
	Charles
微信公众号:
	Charles的皮卡丘
'''
import requests
from ..utils.misc import *
from ..utils.downloader import Downloader


'''咪咕音乐下载类'''
class migu():
	def __init__(self, config, logger_handle, **kwargs):
		self.source = 'migu'
		self.session = requests.Session()
		self.session.proxies.update(config['proxies'])
		self.config = config
		self.logger_handle = logger_handle
		self.__initialize()
	'''歌曲搜索'''
	def search(self, keyword):
		self.logger_handle.info('正在%s中搜索 ——> %s...' % (self.source, keyword))
		cfg = self.config.copy()
		params = {
					'ua': 'Android_migu',
					'version': '5.0.1',
					'text': keyword,
					'pageNo': '1',
					'pageSize': cfg['search_size_per_source'],
					'searchSwitch': '{"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":1}',
				}
		response = self.session.get(self.search_url, headers=self.headers, params=params)
		all_items = response.json()['songResultData']['result']
		songinfos = []
		for item in all_items:
			ext = ''
			download_url = ''
			filesize = '-MB'
			for rate in sorted(item.get('rateFormats', []), key=lambda x: int(x['size']), reverse=True):
				if (int(rate['size']) == 0) or (not rate.get('formatType', '')) or (not rate.get('resourceType', '')): continue
				ext = 'flac' if rate.get('formatType') == 'SQ' else 'mp3'
				download_url = self.player_url.format(copyrightId=item['copyrightId'], 
													  contentId=item['contentId'], 
													  toneFlag=rate['formatType'],
													  resourceType=rate['resourceType'])
				filesize = str(round(int(rate['size'])/1024/1024, 2)) + 'MB'
				break
			if not download_url: continue
			duration = '-:-:-'
			songinfo = {
						'source': self.source,
						'songid': str(item['id']),
						'singers': filterBadCharacter(','.join([s.get('name', '') for s in item.get('singers', [])])),
						'album': filterBadCharacter(item.get('albums', [{'name': '-'}])[0].get('name', '-')),
						'songname': filterBadCharacter(item.get('name', '-')),
						'savedir': cfg['savedir'],
						'savename': '_'.join([self.source, filterBadCharacter(item.get('name', '-'))]),
						'download_url': download_url,
						'filesize': filesize,
						'ext': ext,
						'duration': duration
					}
			songinfos.append(songinfo)
		return songinfos
	'''歌曲下载'''
	def download(self, songinfos):
		for songinfo in songinfos:
			self.logger_handle.info('正在从%s下载 ——> %s...' % (self.source, songinfo['savename']))
			task = Downloader(songinfo, self.session)
			if task.start():
				self.logger_handle.info('成功从%s下载到了 ——> %s...' % (self.source, songinfo['savename']))
			else:
				self.logger_handle.info('无法从%s下载 ——> %s...' % (self.source, songinfo['savename']))
	'''初始化'''
	def __initialize(self):
		self.headers = {
						'Referer': 'https://m.music.migu.cn/', 
						'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
					}
		self.search_url = 'http://pd.musicapp.migu.cn/MIGUM3.0/v1.0/content/search_all.do'
		self.player_url = 'https://app.pd.nf.migu.cn/MIGUM3.0/v1.0/content/sub/listenSong.do?channel=mx&copyrightId={copyrightId}&contentId={contentId}&toneFlag={toneFlag}&resourceType={resourceType}&userId=15548614588710179085069&netType=00'