$TTL 3H
@	IN SOA	@ us.laworks.com. (
					2600    ; serial
					1D	; refresh
					1H	; retry
					1W	; expire
					3H )	; minimum
	NS	@
	A	127.0.0.1
	AAAA	::1

@       IN NS us.laworks.com.

us      IN A 192.168.2.188
dns     IN CNAME us 
www     IN CNAME us
mysql   IN CNAME us

winxp   IN A 192.168.2.177
rhel    IN A 192.168.2.118
test    IN A 192.168.2.123
