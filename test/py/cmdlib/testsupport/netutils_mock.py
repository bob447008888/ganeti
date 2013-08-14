#
#

# Copyright (C) 2013 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.


"""Support for mocking the netutils module"""

import mock

from ganeti import compat
from ganeti import netutils
from cmdlib.testsupport.util import patchModule


# pylint: disable=C0103
def patchNetutils(module_under_test):
  """Patches the L{ganeti.netutils} module for tests.

  This function is meant to be used as a decorator for test methods.

  @type module_under_test: string
  @param module_under_test: the module within cmdlib which is tested. The
        "ganeti.cmdlib" prefix is optional.

  """
  return patchModule(module_under_test, "netutils")


class HostnameMock(object):
  """Simple mocked version of L{netutils.Hostname}.

  """
  def __init__(self, name, ip):
    self.name = name
    self.ip = ip


def _IsOverwrittenReturnValue(value):
  return value is not None and value != mock.DEFAULT and \
      not isinstance(value, mock.Mock)


# pylint: disable=W0613
def _GetHostnameMock(cfg, mock_fct, name=None, family=None):
  if _IsOverwrittenReturnValue(mock_fct.return_value):
    return mock.DEFAULT

  if name is None:
    name = cfg.GetMasterNodeName()

  if name == cfg.GetClusterName():
    cluster = cfg.GetClusterInfo()
    return HostnameMock(cluster.cluster_name, cluster.master_ip)

  node = cfg.GetNodeInfoByName(name)
  if node is not None:
    return HostnameMock(node.name, node.primary_ip)

  return HostnameMock(name, "1.2.3.4")


# pylint: disable=W0613
def _TcpPingMock(cfg, mock_fct, target, port, timeout=None,
                 live_port_needed=None, source=None):
  if _IsOverwrittenReturnValue(mock_fct.return_value):
    return mock.DEFAULT

  if target == cfg.GetClusterName():
    return True
  if cfg.GetNodeInfoByName(target) is not None:
    return True
  if target in [node.primary_ip for node in cfg.GetAllNodesInfo().values()]:
    return True
  if target in [node.secondary_ip for node in cfg.GetAllNodesInfo().values()]:
    return True
  return False


def SetupDefaultNetutilsMock(netutils_mod, cfg):
  """Configures the given netutils_mod mock to work with the given config.

  All relevant functions in netutils_mod are stubbed in such a way that they
  are consistent with the configuration.

  @param netutils_mod: the mock module to configure
  @type cfg: cmdlib.testsupport.ConfigMock
  @param cfg: the configuration to query for netutils request

  """
  netutils_mod.GetHostname.side_effect = \
    compat.partial(_GetHostnameMock, cfg, netutils_mod.GetHostname)
  netutils_mod.TcpPing.side_effect = \
    compat.partial(_TcpPingMock, cfg, netutils_mod.TcpPing)
  netutils_mod.GetDaemonPort.side_effect = netutils.GetDaemonPort
  netutils_mod.FormatAddress.side_effect = netutils.FormatAddress
  netutils_mod.Hostname.GetNormalizedName.side_effect = \
    netutils.Hostname.GetNormalizedName
