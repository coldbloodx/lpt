$TTL 3H
@	IN SOA	@ rname.invalid. (
					2600    ; serial
					1D	; refresh
					1H	; retry
					1W	; expire
					3H )	; minimum
	NS	@
	A	127.0.0.1
	AAAA	::1

@       IN NS rhel.laworks.com.

rhel    IN A 192.168.2.119
dns     IN CNAME rhel
www     IN CNAME rhel
mysql   IN CNAME rhel

winxp   IN A 192.168.2.177
us      IN A 192.168.2.188
test    IN A 192.168.2.123





