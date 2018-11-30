# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import webapp2

from stanwood.external_services.contentful.handlers.clean_up_cached_files import CleanupCachedFilesBaseHandler
from stanwood.external_services.contentful.handlers.contentful_access_token import ContentfulAccessTokenBaseHandler
from stanwood.external_services.contentful.handlers.contentful_download_asset import DownloadAssetBaseHandler
from stanwood.external_services.contentful.handlers.contentful_management_proxy import (
    ContentfulManagementProxyBaseHandler,
)
from stanwood.external_services.contentful.handlers.contentful_proxy import ContentfulProxyBaseHander
from stanwood.external_services.contentful.handlers.files_cache import FilesCacheBaseHandler
from stanwood.external_services.github.handlers import github
from stanwood.handlers import proxy

app = webapp2.WSGIApplication((
    # Contentful
    webapp2.Route(r'/contentful/download/<asset_id:.*>', DownloadAssetBaseHandler),
    webapp2.Route(r'/contentful/files_cache/<source_host:[a-z.]+>/<file_path:.+>', FilesCacheBaseHandler),
    webapp2.Route(r'/contentful/<item_type:\w+>/<item_id:\w+>', ContentfulProxyBaseHander),
    webapp2.Route(r'/contentful/<item_type:\w+>', ContentfulProxyBaseHander),
    webapp2.Route(r'/contentful/', ContentfulProxyBaseHander),
    webapp2.Route(r'/manage/contentful/access_token', ContentfulAccessTokenBaseHandler),
    webapp2.Route(r'/manage/contentful/<endpoint:.*>', ContentfulManagementProxyBaseHandler),
    webapp2.Route(r'/tasks/clean-up', CleanupCachedFilesBaseHandler),
    # github
    webapp2.Route(r'/github/callback', github.GithubTestCallbackHandler, name='github-callback'),
    webapp2.Route(r'/github/authorize', github.GithubAuthorizeHandler),
    # proxy
    webapp2.Route(r'/proxy/<:.*>', proxy.ProxyHandler)
), debug=True)
