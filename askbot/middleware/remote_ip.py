"""Fixes REMOTE_IP meta value
based on the HTTP_X_FORWARDED_FOR value, if used.
Enable this middleware if using django site behind a proxy
server or a load balancer.

Add to the MIDDLEWARE_CLASSES:

    'askbot.middleware.remote_ip.SetRemoteIPFromXForwardedFor',
"""

class SetRemoteIPFromXForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip
