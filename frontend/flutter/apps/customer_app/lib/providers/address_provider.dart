import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:models/models.dart' as models;
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'address_provider.g.dart';

const _keyAddresses = 'saved_addresses';

@riverpod
class SavedAddresses extends _$SavedAddresses {
  @override
  FutureOr<List<models.Address>> build() async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList(_keyAddresses);
    if (list == null || list.isEmpty) return [];
    return list
        .map((e) => models.Address.fromJson(Map<String, dynamic>.from(jsonDecode(e) as Map)))
        .toList();
  }

  Future<void> _persist(List<models.Address> addresses) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _keyAddresses,
      addresses.map((a) => jsonEncode(a.toJson())).toList(),
    );
  }

  Future<void> addAddress(models.Address address) async {
    final list = List<models.Address>.from(state.value ?? []);
    list.add(address);
    state = AsyncValue.data(list);
    await _persist(list);
  }

  Future<void> removeAddress(String id) async {
    final list = List<models.Address>.from(state.value ?? []);
    list.removeWhere((a) => a.id == id);
    if (list.isNotEmpty && list.every((a) => !a.isDefault)) {
      list[0] = list[0].copyWith(isDefault: true);
    }
    state = AsyncValue.data(list);
    await _persist(list);
  }

  Future<void> setDefault(String id) async {
    final list = List<models.Address>.from(state.value ?? []);
    for (var i = 0; i < list.length; i++) {
      list[i] = list[i].copyWith(isDefault: list[i].id == id);
    }
    state = AsyncValue.data(list);
    await _persist(list);
  }

  models.Address? get defaultAddress {
    final list = state.value;
    if (list == null) return null;
    try {
      return list.firstWhere((a) => a.isDefault);
    } catch (_) {
      return list.isNotEmpty ? list.first : null;
    }
  }
}
