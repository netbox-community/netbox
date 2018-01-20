# Setting folder permissions for Image Attachments
In order for Netbox to write to the folder when uploading attachments, you need to modify the folder owner to be netbox (or whatever user you are running Netbox under). Following the instructions thus far provided, complete the following:

```chown -R netbox:netbox /opt/netbox/netbox/media/image-attachments```