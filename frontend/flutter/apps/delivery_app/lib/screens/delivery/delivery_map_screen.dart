import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart' as mb;
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart' as geo;
import 'package:api_client/api_client.dart';
import '../../providers/delivery_provider.dart';
import '../../providers/partner_provider.dart';
import '../../providers/api_providers.dart';

class DeliveryMapScreen extends ConsumerStatefulWidget {
  final String deliveryId;

  const DeliveryMapScreen({super.key, required this.deliveryId});

  @override
  ConsumerState<DeliveryMapScreen> createState() => _DeliveryMapScreenState();
}

class _DeliveryMapScreenState extends ConsumerState<DeliveryMapScreen> {
  mb.MapboxMap? _mapboxMap;

  bool get _isMobile =>
      !kIsWeb && (Platform.isAndroid || Platform.isIOS);

  @override
  Widget build(BuildContext context) {
    final deliveryAsync = ref.watch(deliveryDetailProvider(widget.deliveryId));

    if (!_isMobile) {
      return Scaffold(
        appBar: AppBar(title: const Text('Delivery map')),
        body: const Center(
          child: Text(
            'Map is available on Android and iOS. Use "Open in Maps" for directions.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Map #${widget.deliveryId.substring(0, 8)}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location),
            onPressed: _centerOnUserLocation,
            tooltip: 'Center on my location',
          ),
        ],
      ),
      body: deliveryAsync.when(
        data: (d) {
          if (d == null) {
            return const Center(child: Text('Delivery not found'));
          }
          final hasPickup = d.pickupLat != null && d.pickupLng != null;
          final hasDelivery = d.deliveryLat != null && d.deliveryLng != null;
          if (!hasPickup && !hasDelivery) {
            return const Center(
              child: Text(
                'No coordinates for this delivery. Use "Open in Maps" from details.',
                textAlign: TextAlign.center,
              ),
            );
          }
          final centerLat = hasPickup && hasDelivery
              ? (d.pickupLat! + d.deliveryLat!) / 2
              : (d.pickupLat ?? d.deliveryLat ?? 0.0);
          final centerLng = hasPickup && hasDelivery
              ? (d.pickupLng! + d.deliveryLng!) / 2
              : (d.pickupLng ?? d.deliveryLng ?? 0.0);
          final zoom = (hasPickup && hasDelivery) ? 12.0 : 14.0;
          final camera = mb.CameraOptions(
            center: mb.Point(coordinates: mb.Position(centerLng, centerLat)),
            zoom: zoom,
            bearing: 0,
            pitch: 0,
          );
          return Stack(
            children: [
              mb.MapWidget(
                cameraOptions: camera,
                onMapCreated: (mb.MapboxMap map) {
                  _mapboxMap = map;
                  _fitBoundsAndEnableLocation(d);
                },
              ),
              Positioned(
                left: 16,
                right: 16,
                bottom: 16,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Pickup: ${d.pickupAddress}',
                            style: Theme.of(context).textTheme.bodySmall,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis),
                        const SizedBox(height: 4),
                        Text('Delivery: ${d.deliveryAddress}',
                            style: Theme.of(context).textTheme.bodySmall,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Future<void> _fitBoundsAndEnableLocation(DeliveryDto d) async {
    final map = _mapboxMap;
    if (map == null) return;
    final points = <mb.Point>[];
    if (d.pickupLng != null && d.pickupLat != null) {
      points.add(mb.Point(coordinates: mb.Position(d.pickupLng!, d.pickupLat!)));
    }
    if (d.deliveryLng != null && d.deliveryLat != null) {
      points.add(mb.Point(coordinates: mb.Position(d.deliveryLng!, d.deliveryLat!)));
    }
    if (points.length >= 2) {
      try {
        final centerLat = ((d.pickupLat ?? 0) + (d.deliveryLat ?? 0)) / 2;
        final centerLng = ((d.pickupLng ?? 0) + (d.deliveryLng ?? 0)) / 2;
        final currentCam = mb.CameraOptions(
          center: mb.Point(coordinates: mb.Position(centerLng, centerLat)),
          zoom: 12,
          bearing: 0,
          pitch: 0,
        );
        final cameraOptions = await map.cameraForCoordinatesPadding(
          points,
          currentCam,
          mb.MbxEdgeInsets(top: 100, left: 50, bottom: 150, right: 50),
          null, // maxZoom
          null, // offset
        );
        await map.flyTo(cameraOptions, mb.MapAnimationOptions(duration: 1000));
      } catch (_) {}
    }
    await _enableLocationAndReport(map);
  }

  Future<void> _enableLocationAndReport(mb.MapboxMap map) async {
    if (!_isMobile) return;
    final status = await Permission.locationWhenInUse.request();
    if (!status.isGranted) return;
    if (!mounted) return;
    try {
      await map.location.updateSettings(
        mb.LocationComponentSettings(
          enabled: true,
          pulsingEnabled: true,
          puckBearingEnabled: true,
        ),
      );
    } catch (_) {}
    _reportLocationToBackend();
  }

  Future<void> _reportLocationToBackend() async {
    final partnerId = await ref.read(deliveryPartnerIdProvider.future);
    if (partnerId == null) return;
    try {
      final pos = await geo.Geolocator.getCurrentPosition(
        locationSettings: const geo.LocationSettings(accuracy: geo.LocationAccuracy.medium),
      );
      final service = ref.read(deliveryServiceProvider);
      await service.updatePartnerLocation(
        partnerId: partnerId,
        lat: pos.latitude,
        lng: pos.longitude,
      );
    } catch (_) {}
  }

  Future<void> _centerOnUserLocation() async {
    final map = _mapboxMap;
    if (map == null) return;
    try {
      final pos = await geo.Geolocator.getCurrentPosition(
        locationSettings: const geo.LocationSettings(accuracy: geo.LocationAccuracy.medium),
      );
      await map.flyTo(
        mb.CameraOptions(
          center: mb.Point(coordinates: mb.Position(pos.longitude, pos.latitude)),
          zoom: 16,
          bearing: 0,
          pitch: 0,
        ),
        mb.MapAnimationOptions(duration: 800),
      );
    } catch (_) {}
  }
}
