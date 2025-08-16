import requests
import urllib.parse
import yaml
import json
import base64
import socket
import geoip2.database
import concurrent.futures

def resolve_domain(server_name):
    try:
        if all(c in '0123456789.' for c in server_name):
             return server_name, server_name
        ip = socket.gethostbyname(server_name)
        return server_name, ip
    except (socket.gaierror, UnicodeError, Exception):
        return server_name, server_name

class subs_function:

    def convert_sub_by_post(url: str, output: str, convertor_host="http://0.0.0.0:25500", show_url=False, extra_options=""):
        try:
            print(f"  - Downloading content from: {url}")
            content = requests.get(url, timeout=60).text
            if not content.strip():
                print("  - Downloaded content is empty.")
                return "Err: No nodes found"
        except requests.exceptions.RequestException as e:
            print(f"  - Failed to download subscription: {e}")
            return "Err: failed to download sub"

        try:
            convert_url = f'{convertor_host}/sub?target={output}&insert=false&emoji=true&list=true&tfo=false&scv=true&fdn=false&sort=false{extra_options}'
            headers = {'Content-Type': 'text/plain; charset=utf-8'}
            
            print("  - Posting content to local subconverter for processing...")
            result = requests.post(convert_url, data=content.encode('utf-8'), headers=headers, timeout=240).text
            
            if result == "No nodes were found!":
                return "Err: No nodes found"
            return result
        except Exception as e:
            print(f"  - Failed to convert subscription content: {e}")
            return "Err: failed to parse sub"

    def convert_sub(url: str, output: str, convertor_host="http://0.0.0.0:25500", show_url=False, extra_options=""):
        url = urllib.parse.quote(url, safe='')
        try:
            convert_url = f'{convertor_host}/sub?target={output}&url={url}&insert=false&emoji=true&list=true&tfo=false&scv=true&fdn=false&sort=false{extra_options}'
            result = requests.get(convert_url, timeout=240).text
            if show_url:
                print(f"url to host for {output} : {convert_url}")
            if result == "No nodes were found!":
                return "Err: No nodes found"
            return result

        except Exception as e:
            print(e)
            return "Err: failed to parse sub"

    def is_line_valid(line):
        if (line.startswith("ssr://") or line.startswith("ss://")
                or line.startswith("trojan://") or line.startswith("vmess://") or line.startswith("vless://")):
            return line 
        return ''

    def fix_proxies_name(corresponding_proxies: []):
        emoji = {
            'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬',
            'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
            'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹',
            'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
            'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪',
            'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
            'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳',
            'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
            'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾',
            'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
            'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮',
            'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
            'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻',
            'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
            'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲',
            'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
            'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸',
            'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯',
            'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷',
            'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪',
            'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮',
            'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵',
            'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹',
            'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰',
            'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹',
            'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱',
            'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶',
            'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪',
            'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪',
            'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲',
            'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼',
            'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧',
            'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷',
            'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻',
            'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩',
            'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭',
            'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳',
            'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷',
            'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻',
            'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿',
            'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫',
            'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴',
            'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿',
            'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫',
            'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱',
            'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸',
            'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦',
            'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺',
            'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨',
            'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭',
            'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱',
            'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷',
            'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽',
            'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩',
            'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯',
            'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳',
            'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻',
            'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬',
            'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿',
            'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
            'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫',
            'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹',
            'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼',
            'RELAY': '🏁',
            'NOWHERE': '🇦🇶',
        }

        COUNTRY_NAME_MAPPING = {
            'United States': 'USA',
            'United Kingdom': 'UK',
            'Russian Federation': 'Russia',
            'The Netherlands': 'Netherlands',
            'Türkiye': 'Turkey',
            'United Arab Emirates': 'Emirates'
        }
        
        exclude_list_of_countries = ['IL', 'BH', 'IR']
        
        print("  Step 2.1: Collecting unique domain names for resolution...", flush=True)
        unique_servers = set()
        for item in corresponding_proxies:
            proxy = item.get('c_clash', {})
            if isinstance(proxy, list):
                proxy = proxy[0] if proxy else {}
            server = str(proxy.get('server', ''))
            if server and not all(c in '0123456789.' for c in server):
                unique_servers.add(server)
        print(f"  Found {len(unique_servers)} unique domains to resolve.", flush=True)

        print("  Step 2.2: Resolving domain names concurrently (this may take a moment)...", flush=True)
        resolved_ips = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            future_to_server = {executor.submit(resolve_domain, server): server for server in unique_servers}
            for future in concurrent.futures.as_completed(future_to_server):
                server, ip = future.result()
                resolved_ips[server] = ip
        print("  Step 2.2 COMPLETE. All domains resolved.", flush=True)

        print("  Step 2.3: Renaming proxies with resolved IPs...", flush=True)
        excluded_proxies = []
        with geoip2.database.Reader('./utils/Country.mmdb') as ip_reader:
            total_proxies = len(corresponding_proxies)
            for (index, c_proxy) in enumerate(corresponding_proxies):
                if (index + 1) % 5000 == 0:
                    print(f"  ... Renaming progress: {index + 1}/{total_proxies} nodes processed.", flush=True)

                proxy = c_proxy['c_clash']
                if isinstance(proxy, list): proxy = proxy[0]

                server = str(proxy['server'])
                ip = resolved_ips.get(server, server)

                try:
                    response = ip_reader.country(ip)
                    country_code = response.country.iso_code
                    country_name = response.country.name
                    if not country_name:
                        country_name = country_code or 'Unknown'
                except Exception:
                    ip = '0.0.0.0'
                    country_code = 'NOWHERE'
                    country_name = 'Unknown'

                if country_code == 'CLOUDFLARE':
                    country_code = 'RELAY'
                    country_name = 'Relay'
                elif country_code == 'PRIVATE':
                    country_code = 'RELAY'
                    country_name = 'Relay'
                
                name_emoji = emoji.get(country_code, emoji['NOWHERE'])

                country_name_to_use = COUNTRY_NAME_MAPPING.get(country_name, country_name)
                country_name_formatted = country_name_to_use.replace(' ', '-')
                
                if total_proxies >= 9999:
                    proxy['name'] = f'{name_emoji} {country_name_formatted}-{index:0>5d}'
                elif total_proxies >= 999:
                    proxy['name'] = f'{name_emoji} {country_name_formatted}-{index:0>4d}'
                else:
                    proxy['name'] = f'{name_emoji} {country_name_formatted}-{index:0>3d}'

                c_proxy["c_clash"] = proxy
                
                if country_code in exclude_list_of_countries or name_emoji == emoji['NOWHERE']:
                    excluded_proxies.append(c_proxy)

        print("  Step 2.3 COMPLETE. All proxies renamed.", flush=True)
        return list(filter(lambda c: c not in excluded_proxies, corresponding_proxies))
    
    def fix_proxies_duplication(corresponding_proxies: []):
        print(f"Starting fast de-duplication on {len(corresponding_proxies)} nodes...", flush=True)
        
        seen_fingerprints = set()
        unique_proxies = []
        
        for item in corresponding_proxies:
            proxy = item.get("c_clash")
            if isinstance(proxy, list):
                proxy = proxy[0] if proxy else {}

            fingerprint = (
                proxy.get('server'),
                proxy.get('port'),
                proxy.get('type'),
                proxy.get('cipher'),
                proxy.get('network'),
                proxy.get('obfs'),
                json.dumps(proxy.get('ws-opts', {}), sort_keys=True)
            )

            if fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                unique_proxies.append(item)

        removed_count = len(corresponding_proxies) - len(unique_proxies)
        print(f"Fast de-duplication finished. Removed {removed_count} duplicates. Final count: {len(unique_proxies)}", flush=True)
        
        return unique_proxies
