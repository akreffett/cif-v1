#!/bin/bash
# This script should be edited as necessary and run as root on the machine
# hosting the PostgreSQL server used by CIF

# Tune system shared memory parameters and vm overcommit
page_size=`getconf PAGE_SIZE`
phys_pages=`getconf _PHYS_PAGES`
shmall=$(($phys_pages/2))
shmmax=$(($shmall*$page_size))

cat<<EOF >> ./sysctl.conf
kernel.shmmax = $shmmax
kernel.shmall = $shmall
vm.overcommit_memory = 2
vm.swappiness = 0
EOF

/sbin/sysctl -p

# Set shared buffers and max connections for postgres
sed -i 's/shared_buffers/#shared_buffers/' /var/lib/pgsql/data/postgresql.conf
sed -i 's/max_connections/#max_connections/' /var/lib/pgsql/data/postgresql.conf

total_ram_b=$(($page_size*$phys_pages))
total_ram_kb=$(($total_ram_b/1024))
total_ram_mb=$(($total_ram_kb/1024))
ten_percent_total_ram=$(($total_ram_mb/10))
work_mem=$(($total_ram_mb/8))
[[ $work_mem < 512 ]] && work_mem=512
shared_buffers=$ten_percent_total_ram
effective_cache_size=$(($ten_percent_total_ram*6))

cat<<EOF >> ./postgresql.conf
#------------------------------------------------------------------------------
# CIF Setup                                                                    
#------------------------------------------------------------------------------
# Rough estimates on how to configured postgres to work with large data sets
# See the following URL for proper postgres performance tuning
# http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
wal_buffers = 12MB 		# recommended range for this value is between 2-16MB
work_mem = ${work_mem}MB		# minimum 512MB needed for cif_feed
shared_buffers = ${shared_buffers}MB		# recommended range for this value is 10% on shared db server
checkpoint_segments = 10	# at least 10, 32 is a more common value on dedicated server class hardware
effective_cache_size = ${effective_cache_size}MB	# recommended range for this value is between 60%-80% of your total available RAM
max_connections = 8		# limiting to 8 due to high work_mem value
EOF
