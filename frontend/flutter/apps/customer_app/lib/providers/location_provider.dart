import 'dart:async';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:models/models.dart';

part 'location_provider.g.dart';

/// Simple location state combining current location and selected address.
class LocationState {
  final Location? currentLocation;
  final Address? selectedAddress;

  const LocationState({
    this.currentLocation,
    this.selectedAddress,
  });

  String get displayText {
    if (selectedAddress != null) {
      return selectedAddress!.label.isNotEmpty
          ? selectedAddress!.label
          : selectedAddress!.addressLine1;
    }
    if (currentLocation?.address != null) {
      return currentLocation!.address!;
    }
    return 'Select location';
  }

  LocationState copyWith({
    Location? currentLocation,
    Address? selectedAddress,
  }) {
    return LocationState(
      currentLocation: currentLocation ?? this.currentLocation,
      selectedAddress: selectedAddress ?? this.selectedAddress,
    );
  }
}

@riverpod
class UserLocation extends _$UserLocation {
  @override
  FutureOr<LocationState> build() async {
    // TODO: Load saved address from backend or local storage.
    // For now, start with empty state.
    return const LocationState();
  }

  /// Stub: in future, integrate with geolocator + reverse geocoding.
  Future<void> detectCurrentLocation() async {
    // TODO: Implement real GPS + reverse geocode using geolocator + backend.
    // For now, do nothing and keep placeholder behaviour.
    return;
  }

  Future<void> setSelectedAddress(Address address) async {
    state = AsyncValue.data(
      (state.value ?? const LocationState()).copyWith(
        selectedAddress: address,
      ),
    );
  }
}

