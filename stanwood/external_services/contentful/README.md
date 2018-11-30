1. Requirements:
    - contentful==1.4.1
    - python-jose==1.3.2 (firebase token validation)
    
2. Config.
    ```
    CONTENTFUL_SPACE = os.environ['CONTENTFUL_SPACE']
    CONTENTFUL_TOKEN = os.environ['CONTENTFUL_TOKEN']
    CONTENTFUL_MANAGEMENT_TOKEN = os.environ['CONTENTFUL_MANAGEMENT_TOKEN']
    ```

3. Example file with handlers:
    ```
    import config
    
    from stanwood.external_services.contentful.handlers.clean_up_cached_files import CleanupCachedFilesBaseHandler
    from stanwood.external_services.contentful.handlers.contentful_access_token import ContentfulAccessTokenBaseHandler
    from stanwood.external_services.contentful.handlers.contentful_download_asset import DownloadAssetBaseHandler
    from stanwood.external_services.contentful.handlers.contentful_management_proxy import (
        ContentfulManagementProxyBaseHandler,
    )
    from stanwood.external_services.contentful.handlers.contentful_proxy import ContentfulProxyBaseHander
    from stanwood.external_services.contentful.handlers.files_cache import (
        AssetsFilesCacheBaseHandler,
        FilesCacheBaseHandler,
        ImagesCacheBaseHandler,
    )
    
    
    class AssetsFilesCacheHandler(AssetsFilesCacheBaseHandler):
        pass
    
    
    class CleanupCachedFilesHandler(CleanupCachedFilesBaseHandler):
        pass
    
    
    class DownloadAssetHandler(DownloadAssetBaseHandler):
        CONTENTFUL_SPACE = config.CONTENTFUL_SPACE
        CONTENTFUL_TOKEN = config.CONTENTFUL_TOKEN
    
    
    class ContentfulAccessTokenHandler(ContentfulAccessTokenBaseHandler):
        CONTENTFUL_MANAGEMENT_TOKEN = config.CONTENTFUL_MANAGEMENT_TOKEN
    
    
    class ContentfulManagementProxyHandler(ContentfulManagementProxyBaseHandler):
        CONTENTFUL_MANAGEMENT_TOKEN = config.CONTENTFUL_MANAGEMENT_TOKEN
        CONTENTFUL_SPACE = config.CONTENTFUL_SPACE
    
    
    class ContentfulProxyHandler(ContentfulProxyBaseHander):
        CONTENTFUL_SPACE = config.CONTENTFUL_SPACE
        CONTENTFUL_TOKEN = config.CONTENTFUL_TOKEN
    
    
    class FilesCacheHandler(FilesCacheBaseHandler):
        pass
    
    
    class ImagesCacheHandler(ImagesCacheBaseHandler):
        pass
    ```

4. Example file with routes.
    ```
    import webapp2
    
    from handlers.contentful import CleanupCachedFilesHandler
    from handlers.contentful import ContentfulAccessTokenHandler
    from handlers.contentful import DownloadAssetHandler
    from handlers.contentful import ContentfulManagementProxyHandler
    from handlers.contentful import (
        AssetsFilesCacheHandler,
        FilesCacheHandler,
        ImagesCacheHandler,
    )
    from handlers.contentful import ContentfulProxyHandler
    
    app = webapp2.WSGIApplication((
        webapp2.Route(r'/contentful/images_cache/<file_path:.*>',   ImagesCacheHandler),  # TODO: Remove
        webapp2.Route(r'/contentful/assets_cache/<file_path:.*>',   AssetsFilesCacheHandler),  # TODO: Remove
        webapp2.Route(r'/contentful/files_cache/<source_host:[a-z.]+>/<file_path:.+>',    FilesCacheHandler),
        webapp2.Route(r'/contentful/download/<asset_id:.*>',        DownloadAssetHandler),
        webapp2.Route(r'/contentful/<item_type:\w+>/<item_id:\w+>', ContentfulProxyHandler),
        webapp2.Route(r'/contentful/<item_type:\w+>',               ContentfulProxyHandler),
        webapp2.Route(r'/manage/contentful/access_token',           ContentfulAccessTokenHandler),
        webapp2.Route(r'/manage/contentful/<endpoint:.*>',          ContentfulManagementProxyHandler),
        webapp2.Route(r'/tasks/clean-up',                           CleanupCachedFilesHandler),
    ), debug=True)
    ```

5. Example cron.
    ```
    cron:
    - description: Delete old cached files
      url: /tasks/clean-up
      schedule: every day 2:00
      timezone: Europe/Berlin
    ```
