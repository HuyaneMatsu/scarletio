Resolution configurations implemented

| Name                                  | Key                           | Meaningful    | Implemented   | Comment                                                           |
|---------------------------------------|-------------------------------|---------------|---------------|-------------------------------------------------------------------|
| name_server_configurations            | nameserver                    | true          | true          | -                                                                 |
| option_attempts                       | option attempts               | true          | true          | -                                                                 |
| option_debug                          | option debug                  | false         | false         | Debug mode not planned.                                           |
| option_disable_bind_checking          | option no-check-names         | false         | false         | Seems unnecessary.                                                |
| option_enable_dns_extension           | option edns0                  | true          | false         | Most services ignore keep-alive, so no reason to fully implement. |
| option_force_tcp                      | option use-vc                 | false         | false         | We prefer tls > tcp > udp.                                        |
| option_limit_to_single_request        | option single-request         | true          | true          | -                                                                 |
| option_no_ip_v6_lookups               | option no-aaaa                | true          | true          | -                                                                 |
| option_no_reload                      | option no-reload              | true          | false         | Not really something planned.                                     |
| option_no_unqualified_name_resolving  | option no-tld-query           | true          | false         | What does this even mean?                                         |
| option_prefer_ip_v6                   | option inet6                  | true          | false         | Deprecated since glibc 2.25,                                      |
| option_required_dot_count             | option ndots                  | true          | true          | -                                                                 |
| option_rotate                         | option rotate                 | true          | true          | -                                                                 |
| option_set_verified_data_in_requests  | option trust-ad               | false         | true          | This sets the incoming (?) field, why?                            |
| option_single_request_re_open         | option single-request-reopen  | true          | false         | No keep-alive, so no reopen needed.                               |
| option_timeout                        | option timeout                | true          | true          | -                                                                 |
| searches                              | search                        | true          | false         | -                                                                 |
| sort_list                             | sortlist                      | true          | true          | -                                                                 |
