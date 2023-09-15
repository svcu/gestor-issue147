from django.urls import path
from .views import vehicle, tracker, lease, calendar
from django.views.generic import TemplateView

urlpatterns = [
    # -------------------- Vehicle ----------------------------
    path('create-trailer', vehicle.create_trailer, name='create-trailer'),
    path('list-trailer', vehicle.list_equipment, name='list-trailer'),
    path('select-trailer', vehicle.select_trailer, name='select-trailer'),
    path('update-trailer/<id>', vehicle.update_trailer, name='update-trailer'),
    path('delete-trailer/<id>', vehicle.delete_trailer, name='delete-trailer'),
    path('detail-trailer/<id>', vehicle.detail_trailer, name='detail-trailer'),
    path('select-towit', vehicle.select_towit, name='select-towit'),
    # -------------------- Tracker ----------------------------
    path('create-tracker/<int:trailer_id>',
         tracker.TrackerCreateView.as_view(), name='create-trailer-tracker'),
    path('create-tracker/',
         tracker.TrackerCreateView.as_view(), name='create-tracker'),
    path('update-tracker/<slug:pk>',
         tracker.TrackerUpdateView.as_view(), name='update-tracker'),
    path('delete-tracker/<int:id>',  tracker.delete_tracker, name='delete-tracker'),
    path('detail-tracker/<int:id>',  tracker.tracker_detail, name='detail-tracker'),
    path('trackers-map/',  tracker.trackers, name='trackers-map'),
    path('trackers/',  tracker.trackers_table, name='trackers-table'),
    path('tracker-upload', tracker.tracker_upload, name='tracker-upload'),
    # -------------------- Manufacturer ----------------------------
    path('manufacturer-list', vehicle.manufacturer_list, name='manufacturer-list'),
    path('manufacturer-create/', vehicle.manufacturer_create,
         name='manufacturer-create'),
    path('manufacturer-update/<int:pk>',
         vehicle.manufacturer_update, name='manufacturer-update'),
    path('manufacturer-delete/<int:pk>',
         vehicle.manufacturer_delete, name='manufacturer-delete'),
    # -------------------- Picture ----------------------------
    path('picture/create/<int:trailer_id>',
         vehicle.trailer_picture_create, name='trailer-picture-create'),
    path('share_pictures/<ids>',  vehicle.share_pictures, name='share-pictures'),
    path('delete_trailer_pictures/<ids>',
         vehicle.delete_trailer_pictures, name='delete-trailer-pictures'),
    path('update_pinned_picture/<int:pk>/',
         vehicle.update_pinned_picture, name='update-pinned-picture'),
    # -------------------- Document ----------------------------
    path('document/create/<int:trailer_id>',
         vehicle.create_document, name='trailer-document-create'),
    path('update_trailer_document/<id>',
         vehicle.update_document, name='update-trailer-document'),
    path('delete_trailer_document/<id>',
         vehicle.delete_document, name='delete-trailer-document'),
    # -------------------- Contracts ----------------------------
    path('create_contract/<int:lessee_id>/<int:trailer_id>/',
         lease.lease_create_view, name='create-contract'),
    path('contract/<int:id>',  lease.contract_detail, name='detail-contract'),
    path('contract_signing/<int:id>',
         lease.contract_signing, name='contract-signing'),
    path('select_lessee/<int:trailer_id>/',
         lease.select_lessee, name='select-lessee'),
    path('update_lesee/<int:trailer_id>/<int:lessee_id>/',
         lease.update_lessee, name='update-lessee'),
    path('create_lesee/<int:trailer_id>/',
         lease.update_lessee, name='create-lessee'),
    path('create_lessee_data/<int:trailer_id>/<int:lessee_id>/',
         lease.create_lessee_data, name='update-lessee-data'),
    path('update_lessee_data/<slug:pk>',
         lease.LeseeDataUpdateView.as_view(), name='update-lessee-data'),
    path('contract_pdf/<int:id>',  lease.contract_pdf,
         name='contract-signed'),
    path('contracts/',  lease.contracts, name='contracts'),
    path('update_contract/<slug:pk>',
         lease.ContractUpdateView.as_view(), name='update-contract'),
    path('update_contract_stage/<slug:id>/<stage>',
         lease.update_contract_stage, name='update-contract-stage'),
    path('capture_signature/<lease_id>/<position>',
         lease.create_handwriting, name='capture-signature'),
    path('capture_signature/<lease_id>/<position>/<external>',
         lease.create_handwriting, name='capture-signature'),
    # -------------------- Inspection ----------------------------
    path('create_inspection/<lease_id>/',
         lease.create_inspection, name='create-inspection'),
    path('update_inspection/<id>/',
         lease.update_inspection, name='update-inspection'),
    path('update_tires/<inspection_id>/',
         lease.update_tires, name='update-tires'),
    # -------------------- Calendar ----------------------------
    # path('erp/schedule/', include('schedule.urls')),
    path('api_occurrences/', calendar.api_occurrences, name='api-occurrences'),
    path('calendar/', calendar.calendar_week,  name='calendar'),
]
